"""
Agendador para atualização periódica do cache usando Discord Tasks.
"""

import asyncio
import logging
from datetime import datetime
from nextcord.ext import tasks

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager

logger = logging.getLogger(__name__)


class CacheScheduler:
    """Gerencia a atualização periódica do cache usando Discord Tasks."""
    
    def __init__(self, api_client: PandaScoreClient, cache_manager: MatchCacheManager, notification_manager=None):
        """
        Inicializa o agendador.
        
        Args:
            api_client: Cliente da API PandaScore
            cache_manager: Gerenciador de cache
            notification_manager: Gerenciador de notificações (opcional)
        """
        self.api_client = api_client
        self.cache_manager = cache_manager
        self.notification_manager = notification_manager
        self.is_running = False
        
        logger.info("⏰ CacheScheduler inicializado (Discord Tasks)")
    
    async def update_all_matches(self):
        """Atualiza todas as partidas (upcoming, running, past e canceladas)."""
        try:
            logger.info("🔄 Iniciando atualização completa do cache...")
            
            all_matches = []
            
            # Buscar partidas próximas
            try:
                upcoming = await self.api_client.get_upcoming_matches(per_page=50)
                all_matches.extend(upcoming)
                logger.info(f"  ✓ {len(upcoming)} partidas próximas obtidas")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar partidas próximas: {e}")
            
            # Buscar partidas ao vivo
            try:
                running = await self.api_client.get_running_matches()
                all_matches.extend(running)
                logger.info(f"  ✓ {len(running)} partidas ao vivo obtidas")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar partidas ao vivo: {e}")
            
            # Buscar partidas passadas (finalizadas)
            try:
                past = await self.api_client.get_past_matches(hours=24, per_page=20)
                all_matches.extend(past)
                logger.info(f"  ✓ {len(past)} partidas finalizadas obtidas")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar partidas finalizadas: {e}")
            
            # Buscar partidas canceladas/adiadas
            try:
                canceled = await self.api_client.get_canceled_matches(per_page=20)
                all_matches.extend(canceled)
                logger.info(f"  ✓ {len(canceled)} partidas canceladas/adiadas obtidas")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar partidas canceladas/adiadas: {e}")
            
            # Cachear todas as partidas
            if all_matches:
                stats = await self.cache_manager.cache_matches(all_matches, "all")
                logger.info(f"✓ Cache atualizado: {stats['added']} novas, {stats['updated']} atualizadas")
                
                # Agendar lembretes para as novas partidas
                if self.notification_manager and stats['added'] > 0:
                    for match in all_matches:
                        try:
                            # Agendar para todos os servidores que têm notificações ativadas
                            client = await self.cache_manager.get_client()
                            result = await client.execute(
                                "SELECT guild_id FROM guild_config WHERE notify_upcoming = 1 OR notify_live = 1"
                            )
                            
                            if result.rows:
                                for row in result.rows:
                                    guild_id = row[0]
                                    await self.notification_manager.setup_reminders_for_match(guild_id, match)
                        except Exception as e:
                            logger.error(f"Erro ao agendar lembretes: {e}")
            else:
                logger.warning("⚠️ Nenhuma partida obtida da API")
            
            # Limpar cache antigo (> 24h)
            deleted = await self.cache_manager.clean_old_cache(hours=24)
            if deleted > 0:
                logger.info(f"🗑️ {deleted} partidas antigas removidas")
            
            # Mostrar estatísticas
            stats = await self.cache_manager.get_cache_stats()
            logger.info(f"📊 Cache: {stats.get('total_matches', 0)} partidas | "
                       f"{stats.get('live_matches', 0)} ao vivo | "
                       f"{stats.get('upcoming_matches', 0)} próximas")
            
        except Exception as e:
            logger.error(f"✗ Erro na atualização do cache: {e}")
            import traceback
            traceback.print_exc()
    
    async def update_live_matches(self):
        """Atualiza apenas partidas ao vivo (mais frequente)."""
        try:
            logger.info("🔴 Atualizando partidas ao vivo...")
            
            running = await self.api_client.get_running_matches()
            
            if running:
                stats = await self.cache_manager.cache_matches(running, "running")
                logger.info(f"✓ {len(running)} partidas ao vivo atualizadas")
            else:
                logger.info("ℹ️ Nenhuma partida ao vivo no momento")
                
        except Exception as e:
            logger.error(f"✗ Erro ao atualizar partidas ao vivo: {e}")
            import traceback
            traceback.print_exc()
    
    # Task: Atualização completa a cada 15 minutos
    @tasks.loop(minutes=15)
    async def update_all_task(self):
        """Task do Discord para atualização completa."""
        await self.update_all_matches()
    
    # Task: Atualização de partidas ao vivo a cada 5 minutos
    @tasks.loop(minutes=5)
    async def update_live_task(self):
        """Task do Discord para atualização de partidas ao vivo."""
        await self.update_live_matches()
    
    @update_all_task.before_loop
    async def before_update_all(self):
        """Aguarda o bot estar pronto antes de iniciar a task."""
        logger.info("⏳ Aguardando bot ficar pronto...")
        await asyncio.sleep(2)  # Pequeno delay para garantir que tudo está inicializado
    
    @update_live_task.before_loop
    async def before_update_live(self):
        """Aguarda o bot estar pronto antes de iniciar a task."""
        await asyncio.sleep(2)
    
    def start(self):
        """Inicia as tasks."""
        if self.is_running:
            logger.warning("⚠️ Agendador já está rodando")
            return
        
        # Iniciar ambas as tasks
        self.update_all_task.start()
        self.update_live_task.start()
        
        self.is_running = True
        
        logger.info("✓ Agendador iniciado com Discord Tasks!")
        logger.info("  • Atualização completa: a cada 15 minutos")
        logger.info("  • Partidas ao vivo: a cada 5 minutos")
        logger.info("  • Primeira execução: em 2 segundos")
    
    def stop(self):
        """Para as tasks."""
        if not self.is_running:
            logger.warning("⚠️ Agendador não está rodando")
            return
        
        # Parar tasks do Discord
        self.update_all_task.cancel()
        self.update_live_task.cancel()
        
        self.is_running = False
        logger.info("✓ Agendador parado")
    
    def get_next_run_time(self, task_name: str) -> str:
        """
        Retorna próxima execução de uma task.
        
        Args:
            task_name: Nome da task (update_all ou update_live)
            
        Returns:
            String com data/hora da próxima execução
        """
        if task_name == "update_all" and self.update_all_task.next_iteration:
            return self.update_all_task.next_iteration.strftime("%Y-%m-%d %H:%M:%S")
        elif task_name == "update_live" and self.update_live_task.next_iteration:
            return self.update_live_task.next_iteration.strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"
