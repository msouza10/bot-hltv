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

# Cache em memória para respostas rápidas
_memory_cache = {
    "upcoming": None,
    "running": None,
    "finished": None,
    "stats": None,
    "last_update": None
}


class MatchCacheManager:
    """Gerencia o cache de partidas no libSQL."""
    
    # Timeout para queries (3 segundos para não quebrar discord interactions)
    QUERY_TIMEOUT = 3.0
    
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
                        
                        # Cachear streams da partida se disponível
                        streams_list = match.get("streams_list", [])
                        if streams_list:
                            await self.cache_streams(match_id, streams_list, source="pandascore")
                        
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
                
                # Atualizar cache em memória para respostas rápidas
                try:
                    await self._update_memory_cache(client)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao atualizar cache em memória: {e}")
                
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
            status: Filtrar por status (not_started, running, finished, ou 'results' para finished+canceled+postponed)
            hours: Últimas X horas
            limit: Limite de resultados
            
        Returns:
            Lista de partidas
        """
        try:
            client = await self.get_client()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            if status == "results":
                # Para /resultados: incluir finished, canceled, postponed
                # Usar COALESCE(begin_at, updated_at) porque begin_at é NULL para finished
                query = await asyncio.wait_for(
                    client.execute("""
                        SELECT match_data
                        FROM matches_cache
                        WHERE status IN ('finished', 'canceled', 'postponed')
                          AND updated_at >= ?
                        ORDER BY COALESCE(begin_at, updated_at) DESC
                        LIMIT ?
                    """, [cutoff, limit]),
                    timeout=self.QUERY_TIMEOUT
                )
            elif status:
                query = await asyncio.wait_for(
                    client.execute("""
                        SELECT match_data
                        FROM matches_cache
                        WHERE status = ?
                          AND updated_at >= ?
                        ORDER BY begin_at ASC
                        LIMIT ?
                    """, [status, cutoff, limit]),
                    timeout=self.QUERY_TIMEOUT
                )
            else:
                query = await asyncio.wait_for(
                    client.execute("""
                        SELECT match_data
                        FROM matches_cache
                        WHERE updated_at >= ?
                        ORDER BY begin_at ASC
                        LIMIT ?
                    """, [cutoff, limit]),
                    timeout=self.QUERY_TIMEOUT
                )
            
            matches = [json.loads(row["match_data"]) for row in query.rows]
            return matches
            
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ Timeout ao buscar partidas do cache (timeout={self.QUERY_TIMEOUT}s)")
            return []
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
    
    async def _update_memory_cache(self, client):
        """Atualiza cache em memória com dados do banco para respostas rápidas."""
        global _memory_cache
        
        try:
            logger.debug("🔄 Iniciando atualização do cache em memória...")
            
            # Próximas partidas
            logger.debug("  1. Buscando upcoming...")
            result = await asyncio.wait_for(
                client.execute("""
                    SELECT match_data FROM matches_cache
                    WHERE status = 'not_started'
                    ORDER BY begin_at ASC LIMIT 50
                """),
                timeout=10.0
            )
            _memory_cache["upcoming"] = [
                json.loads(row["match_data"]) for row in result.rows
            ]
            logger.debug(f"    ✓ {len(_memory_cache['upcoming'])} upcoming matches")
            
            # Partidas ao vivo
            logger.debug("  2. Buscando running...")
            result = await asyncio.wait_for(
                client.execute("""
                    SELECT match_data FROM matches_cache
                    WHERE status = 'running'
                    ORDER BY begin_at DESC LIMIT 10
                """),
                timeout=10.0
            )
            _memory_cache["running"] = [
                json.loads(row["match_data"]) for row in result.rows
            ]
            logger.debug(f"    ✓ {len(_memory_cache['running'])} running matches")
            
            # Resultados recentes (finished + canceled + postponed)
            logger.debug("  3. Buscando finished...")
            result = await asyncio.wait_for(
                client.execute("""
                    SELECT match_data FROM matches_cache
                    WHERE status IN ('finished', 'canceled', 'postponed')
                    ORDER BY begin_at DESC LIMIT 20
                """),
                timeout=10.0
            )
            _memory_cache["finished"] = [
                json.loads(row["match_data"]) for row in result.rows
            ]
            logger.debug(f"    ✓ {len(_memory_cache['finished'])} finished matches")
            
            _memory_cache["last_update"] = datetime.now()
            logger.debug("✓ Cache em memória atualizado com sucesso")
            
        except asyncio.TimeoutError:
            logger.warning("⚠️ Timeout ao atualizar cache em memória")
        except Exception as e:
            logger.error(f"✗ Erro ao atualizar cache em memória: {e}")
    
    async def get_cached_matches_fast(self, status: str, limit: int = 50) -> List[Dict]:
        """
        Obtém partidas do cache em memória (muito rápido!).
        
        Args:
            status: 'upcoming', 'running', ou 'finished'
            limit: Limite de resultados
            
        Returns:
            Lista de partidas (pode estar vazia se nunca foi atualizado)
        """
        global _memory_cache
        
        if status == "not_started":
            status = "upcoming"
        
        matches = _memory_cache.get(status) or []
        return matches[:limit]
    
    async def cache_streams(self, match_id: int, streams_list: List[Dict], source: str = "pandascore") -> bool:
        """
        Armazena streams de uma partida no cache.
        
        ⚠️ IMPORTANTE: NÃO usa self._lock aqui! É chamado dentro de cache_matches()
        que já tem o lock, para evitar deadlock.
        
        Args:
            match_id: ID da partida
            streams_list: Lista de streams da API PandaScore
            source: Origem dos streams ('pandascore' ou 'twitch_search')
            
        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            # Validação
            if not streams_list:
                logger.debug(f"   ⚠️  Nenhum stream para match {match_id}")
                return True  # Não é erro, apenas sem streams
            
            client = await self.get_client()
            
            # Limpar streams antigos da partida
            await client.execute(
                "DELETE FROM match_streams WHERE match_id = ?",
                [match_id]
            )
            
            # Mapa de emojis de origem
            source_emoji = {
                "pandascore": "🌐",  # API
                "twitch_search": "🔍",  # Busca manual
            }
            emoji = source_emoji.get(source, "📡")
            source_label = "PandaScore API" if source == "pandascore" else "Busca Manual (Twitch)"
            
            # Inserir novos streams
            cached_count = 0
            for stream in streams_list:
                # Garantir que tem raw_url
                raw_url = stream.get("raw_url", "").strip()
                if not raw_url:
                    logger.warning(f"   ⚠️  Stream sem raw_url em match {match_id}: {stream}")
                    continue
                
                platform = self._extract_platform(raw_url)
                channel_name = self._extract_channel_name(raw_url)
                
                # 🎥 NOVO: Para YouTube, tentar buscar o nome real do canal via API
                # Isso cobre: watch?v=..., youtu.be/..., @channel, c/channel, etc
                if platform == "youtube":
                    try:
                        from src.services.youtube_service import get_youtube_service
                        youtube_svc = get_youtube_service()
                        real_channel_name = await youtube_svc.get_channel_name(raw_url)
                        if real_channel_name:
                            # Atualizar com nome real
                            old_name = channel_name
                            channel_name = real_channel_name
                            logger.info(f"   🎥 YouTube: '{old_name}' → '{real_channel_name}' (Match {match_id})")
                        else:
                            logger.debug(f"   🎥 Não foi possível obter nome real para: {raw_url}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Erro ao buscar nome do canal YouTube: {e}")
                        # Continua com o nome extraído, não falha
                
                # Debug: log de cada stream sendo cacheado com origem
                logger.debug(f"   {emoji} Match {match_id}: {platform} / {channel_name} ({stream.get('language')}) [{source_label}]")
                
                # Usar embed_url se tiver, senão usar raw_url como fallback
                url_for_db = stream.get("embed_url") or raw_url
                
                await client.execute(
                    """INSERT INTO match_streams 
                       (match_id, platform, channel_name, url, raw_url, language, is_official, is_main, is_automated, viewer_count, title)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        match_id,
                        platform,
                        channel_name,
                        url_for_db,
                        raw_url,
                        stream.get("language", "unknown"),
                        1 if stream.get("official", False) else 0,
                        1 if stream.get("main", False) else 0,
                        1 if stream.get("is_automated", False) else 0,
                        stream.get("viewer_count", 0) or 0,
                        stream.get("title", "") or ""
                    ]
                )
                cached_count += 1
            
            logger.info(f"   {emoji} {cached_count} stream(s) cacheado(s) para match {match_id} [{source_label}]")
            return True
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao cachear streams para match {match_id}")
            return False
        except Exception as e:
                logger.error(f"✗ Erro ao cachear streams: {e}")
                return False
    
    async def get_match_streams(self, match_id: int) -> List[Dict]:
        """
        Obtém streams de uma partida do cache.
        
        Args:
            match_id: ID da partida
            
        Returns:
            Lista de dicts com informações dos streams
        """
        try:
            client = await self.get_client()
            
            result = await asyncio.wait_for(
                client.execute(
                    """SELECT platform, channel_name, url, raw_url, language, is_official, is_main, is_automated, viewer_count, title
                       FROM match_streams
                       WHERE match_id = ?
                       ORDER BY is_main DESC, is_official DESC, language ASC""",
                    [match_id]
                ),
                timeout=self.QUERY_TIMEOUT
            )
            
            streams = []
            for row in result.rows:
                streams.append({
                    "platform": row[0],
                    "channel_name": row[1],
                    "url": row[2],
                    "raw_url": row[3],
                    "language": row[4],
                    "is_official": bool(row[5]),
                    "is_main": bool(row[6]),
                    "is_automated": bool(row[7]) if row[7] is not None else False,
                    "viewer_count": row[8] if row[8] is not None else 0,
                    "title": row[9] if row[9] is not None else ""
                })
            
            return streams
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar streams para match {match_id}")
            return []
        except Exception as e:
            logger.error(f"✗ Erro ao buscar streams: {e}")
            return []
    
    async def get_guild_timezone(self, guild_id: int) -> Optional[str]:
        """
        Obtém o timezone configurado para um servidor (guild).
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            Timezone (ex: 'America/Sao_Paulo') ou None se não configurado
        """
        try:
            client = await self.get_client()
            
            result = await asyncio.wait_for(
                client.execute(
                    "SELECT timezone FROM guild_config WHERE guild_id = ?",
                    [guild_id]
                ),
                timeout=self.QUERY_TIMEOUT
            )
            
            if result.rows and len(result.rows) > 0:
                timezone = result.rows[0][0]
                return timezone if timezone else None
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar timezone para guild {guild_id}")
            return None
        except Exception as e:
            logger.error(f"✗ Erro ao buscar timezone: {e}")
            return None
    
    @staticmethod
    def _extract_platform(url: str) -> str:
        """
        Extrai a plataforma da URL da stream.
        
        Args:
            url: URL bruta da stream
            
        Returns:
            Nome da plataforma (twitch, kick, youtube, etc)
        """
        url_lower = url.lower()
        if "twitch.tv" in url_lower:
            return "twitch"
        elif "kick.com" in url_lower:
            return "kick"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "facebook.com" in url_lower or "fb.watch" in url_lower:
            return "facebook"
        else:
            return "other"
    
    @staticmethod
    def _extract_channel_name(url: str) -> str:
        """
        Extrai o nome do canal da URL da stream.
        
        Args:
            url: URL bruta da stream
            
        Returns:
            Nome do canal
        """
        # Remove protocolo
        url = url.replace("https://", "").replace("http://", "")
        
        # Para Twitch: www.twitch.tv/channel_name
        if "twitch.tv" in url:
            parts = url.split("/")
            channel = parts[-1] if len(parts) > 1 else "unknown"
            return channel.split("?")[0].split("#")[0]  # Remove query params
        
        # Para Kick: kick.com/channel_name
        elif "kick.com" in url:
            parts = url.split("/")
            channel = parts[-1] if len(parts) > 1 else "unknown"
            return channel.split("?")[0].split("#")[0]  # Remove query params
        
        # Para YouTube: youtube.com/c/channel_name ou youtube.com/@channel_name ou watch?v=...
        elif "youtube.com" in url or "youtu.be" in url:
            # Se é um link de canal (youtube.com/c/... ou youtube.com/@...)
            if "/c/" in url or "/@" in url:
                parts = url.split("/")
                for i, part in enumerate(parts):
                    if part in ["c"] or part.startswith("@"):
                        channel = parts[i + 1] if i + 1 < len(parts) else "unknown"
                        return channel.split("?")[0].split("#")[0]
            # Se é um link short do YouTube (youtu.be/...) - é sempre um vídeo
            if "youtu.be" in url:
                return "YouTube"
            # Se é um link de vídeo (watch?v=...) - é sempre um vídeo
            if "watch?v=" in url or "/videos" in url or "/live" in url:
                return "YouTube"
            return "YouTube"
        
        # Para Facebook
        elif "facebook.com" in url or "fb.watch" in url:
            parts = url.split("/")
            channel = parts[-1] if len(parts) > 1 else "unknown"
            return channel.split("?")[0].split("#")[0]  # Remove query params
        
        else:
            return "unknown"

