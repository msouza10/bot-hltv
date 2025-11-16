"""
Gerenciador de cache para partidas usando libSQL (Turso).
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import libsql_client

logger = logging.getLogger(__name__)


class MatchCacheManager:
    """Gerencia o cache de partidas no libSQL."""
    
    def __init__(self, db_url: str, auth_token: Optional[str] = None):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            db_url: URL do banco libSQL (file:path.db ou libsql://...)
            auth_token: Token de autenticação (opcional, necessário para Turso remoto)
        """
        self.db_url = db_url
        self.auth_token = auth_token
        self._lock = asyncio.Lock()
        self._client = None
        
        logger.info(f"📦 MatchCacheManager inicializado: {db_url}")
    
    async def get_client(self):
        """Obtém ou cria cliente libSQL."""
        if self._client is None:
            if self.auth_token:
                self._client = libsql_client.create_client(
                    url=self.db_url,
                    auth_token=self.auth_token
                )
            else:
                self._client = libsql_client.create_client(url=self.db_url)
        return self._client
    
    async def close(self):
        """Fecha conexão com o banco."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def cache_matches(self, matches: List[Dict], update_type: str = "all") -> Dict:
        """
        Armazena partidas no cache.
        
        Args:
            matches: Lista de partidas da API
            update_type: Tipo de atualização (upcoming, running, past, all)
            
        Returns:
            Dict com estatísticas da operação
        """
        stats = {"updated": 0, "added": 0, "errors": 0}
        
        async with self._lock:
            try:
                client = await self.get_client()
                
                for match in matches:
                    try:
                        match_id = match.get("id")
                        if not match_id:
                            continue
                        
                        match_data = json.dumps(match)
                        status = match.get("status", "not_started")
                        tournament_name = match.get("tournament", {}).get("name")
                        begin_at = match.get("begin_at")
                        end_at = match.get("end_at")
                        
                        # Verificar se existe
                        result = await client.execute(
                            "SELECT match_id FROM matches_cache WHERE match_id = ?",
                            [match_id]
                        )
                        exists = len(result.rows) > 0
                        
                        # Inserir ou atualizar
                        await client.execute("""
                            INSERT INTO matches_cache 
                                (match_id, match_data, status, tournament_name, begin_at, end_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                            ON CONFLICT(match_id) DO UPDATE SET
                                match_data = excluded.match_data,
                                status = excluded.status,
                                tournament_name = excluded.tournament_name,
                                begin_at = excluded.begin_at,
                                end_at = excluded.end_at,
                                updated_at = CURRENT_TIMESTAMP
                        """, [match_id, match_data, status, tournament_name, begin_at, end_at])
                        
                        if exists:
                            stats["updated"] += 1
                        else:
                            stats["added"] += 1
                            
                    except Exception as e:
                        logger.error(f"✗ Erro ao cachear partida {match.get('id')}: {e}")
                        stats["errors"] += 1
                
                # Registrar atualização
                await client.execute("""
                    INSERT INTO cache_update_log 
                        (update_type, matches_updated, matches_added, status, completed_at)
                    VALUES (?, ?, ?, 'success', CURRENT_TIMESTAMP)
                """, [update_type, stats["updated"], stats["added"]])
                
                return stats
                
            except Exception as e:
                logger.error(f"✗ Erro ao atualizar cache: {e}")
                raise
    
    async def get_cached_matches(
        self,
        status: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """
        Obtém partidas do cache.
        
        Args:
            status: Filtrar por status (not_started, running, finished)
            hours: Últimas X horas
            limit: Limite de resultados
            
        Returns:
            Lista de partidas
        """
        try:
            client = await self.get_client()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            if status:
                result = await client.execute("""
                    SELECT match_data
                    FROM matches_cache
                    WHERE status = ?
                      AND updated_at >= ?
                    ORDER BY begin_at ASC
                    LIMIT ?
                """, [status, cutoff, limit])
            else:
                result = await client.execute("""
                    SELECT match_data
                    FROM matches_cache
                    WHERE updated_at >= ?
                    ORDER BY begin_at ASC
                    LIMIT ?
                """, [cutoff, limit])
            
            matches = [json.loads(row["match_data"]) for row in result.rows]
            return matches
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter matches do cache: {e}")
            return []
    
    async def clean_old_cache(self, hours: int = 24) -> int:
        """
        Remove partidas antigas do cache.
        
        Args:
            hours: Remover partidas finalizadas há mais de X horas
            
        Returns:
            Número de partidas removidas
        """
        try:
            client = await self.get_client()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            result = await client.execute("""
                DELETE FROM matches_cache
                WHERE status = 'finished'
                  AND (end_at < ? OR updated_at < ?)
                RETURNING match_id
            """, [cutoff, cutoff])
            
            deleted = len(result.rows)
            return deleted
            
        except Exception as e:
            logger.error(f"✗ Erro ao limpar cache: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict:
        """
        Obtém estatísticas do cache.
        
        Returns:
            Dict com estatísticas
        """
        try:
            client = await self.get_client()
            result = await client.execute("SELECT * FROM cache_stats")
            
            if result.rows:
                # Row é como um dict, acesso direto por chave
                row = result.rows[0]
                return {
                    "total_matches": row["total_matches"] or 0,
                    "live_matches": row["live_matches"] or 0,
                    "upcoming_matches": row["upcoming_matches"] or 0,
                    "finished_matches": row["finished_matches"] or 0,
                    "recently_updated": row["recently_updated"] or 0,
                    "newest_update": row["newest_update"] or "N/A"
                }
            return {}
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter estatísticas: {e}")
            return {}
    
    async def is_cache_stale(self, minutes: int = 15) -> bool:
        """
        Verifica se o cache está desatualizado.
        
        Args:
            minutes: Minutos desde última atualização
            
        Returns:
            True se desatualizado
        """
        try:
            client = await self.get_client()
            
            cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            result = await client.execute("""
                SELECT COUNT(*) as count FROM matches_cache
                WHERE updated_at >= ?
            """, [cutoff])
            
            count = result.rows[0]["count"]
            return count == 0
            
        except Exception as e:
            logger.error(f"✗ Erro ao verificar cache: {e}")
            return True
