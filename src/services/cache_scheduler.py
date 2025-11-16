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
            
            # 🔥 VALIDAÇÃO DE TRANSIÇÕES DE ESTADO
            # Detecta partidas que mudaram de running → finished
            await self.validate_state_transitions(all_matches)
            
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
    
    async def validate_state_transitions(self, all_matches):
        """
        Valida transições de estado das partidas.
        Detecta se alguma partida mudou de 'running' para 'finished'
        e atualiza o cache automaticamente.
        """
        try:
            # Extrair IDs das partidas atuais
            current_ids = {match.get('id'): match for match in all_matches}
            
            # Buscar partidas em cache que estão com status 'running'
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT match_id, status FROM matches_cache WHERE status = 'running'"
            )
            
            cached_running = {row[0]: row[1] for row in (result.rows or [])}
            
            # Comparar
            transitions = []
            for match_id, cached_status in cached_running.items():
                if match_id not in current_ids:
                    # Partida running não está na lista atualizada
                    # Isso significa que ela pode ter mudado de status
                    transitions.append(match_id)
            
            if not transitions:
                logger.info("✅ Nenhuma transição de estado detectada")
                return
            
            logger.warning(f"🔄 {len(transitions)} partida(s) com possível mudança de estado")
            
            # Para cada partida com possível transição
            for match_id in transitions:
                logger.info(f"   🔍 Verificando partida {match_id}...")
                
                try:
                    # Procurar em finished
                    for match in all_matches:
                        if match.get('id') == match_id:
                            old_status = cached_running[match_id]
                            new_status = match.get('status')
                            
                            if old_status != new_status:
                                logger.warning(f"      🔴 TRANSIÇÃO DETECTADA: {old_status} → {new_status}")
                                logger.warning(f"         Match: {match.get('name')}")
                                logger.warning(f"         Resultado: {match.get('results', [])}")
                                
                                # Atualizar no cache
                                await self.cache_manager.cache_matches([match], "transition")
                                logger.info(f"      ✅ Cache atualizado!")
                            break
                    else:
                        logger.info(f"      ℹ️  Partida {match_id} não encontrada na atualização")
                
                except Exception as e:
                    logger.error(f"      ✗ Erro ao validar transição: {e}")
        
        except Exception as e:
            logger.error(f"✗ Erro ao validar transições de estado: {e}")
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
                
                # 🔥 VALIDAÇÃO IMEDIATA: Verificar se alguma running virou finished
                await self.check_running_to_finished_transitions(running)
            else:
                logger.info("ℹ️ Nenhuma partida ao vivo no momento")
            
            # Detectar partidas travadas (running há muito tempo sem atualização)
            await self.detect_and_fix_stuck_matches()
                
        except Exception as e:
            logger.error(f"✗ Erro ao atualizar partidas ao vivo: {e}")
            import traceback
            traceback.print_exc()
    
    async def check_running_to_finished_transitions(self, running_matches):
        """
        Verifica se alguma partida em 'running' mudou para 'finished'
        Executa a cada 5 minutos junto com update_live_matches
        """
        try:
            if not running_matches:
                return
            
            running_ids = {m.get('id') for m in running_matches}
            
            # Buscar partidas finished recentes
            finished = await self.api_client.get_past_matches(hours=2, per_page=50)
            finished_ids = {m.get('id') for m in finished}
            
            # Procurar por IDs que estão em finished mas não em running
            # Isso indica que saíram de running
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT match_id FROM matches_cache WHERE status = 'running'"
            )
            
            cached_running_ids = {row[0] for row in (result.rows or [])}
            
            # Encontrar partidas que estavam running mas agora estão finished
            transitions = cached_running_ids & finished_ids - running_ids
            
            if not transitions:
                return
            
            logger.warning(f"🔥 {len(transitions)} partida(s) mudou de RUNNING → FINISHED")
            
            for finished_match in finished:
                if finished_match.get('id') in transitions:
                    match_id = finished_match.get('id')
                    logger.warning(f"   🔴 {finished_match.get('name')}")
                    logger.warning(f"      ID: {match_id}")
                    logger.warning(f"      Status: {finished_match.get('status')}")
                    logger.warning(f"      Resultado: {finished_match.get('results', [])}")
                    
                    # Atualizar imediatamente no cache
                    await self.cache_manager.cache_matches([finished_match], "live_transition")
                    logger.info(f"      ✅ Cache atualizado!")
        
        except Exception as e:
            logger.error(f"✗ Erro ao verificar transições running→finished: {e}")
            import traceback
            traceback.print_exc()
    
    async def detect_and_fix_stuck_matches(self):
        """
        Detecta partidas com status 'running' que estão travadas por muito tempo.
        Verifica na API se mudaram para 'finished' e atualiza o cache.
        """
        try:
            logger.info("🔍 Verificando se há partidas travadas (running)...")
            
            # Buscar partidas running há mais de 2 horas
            client = await self.cache_manager.get_client()
            result = await client.execute("""
                SELECT id, match_id, begin_at, updated_at 
                FROM matches_cache 
                WHERE status = 'running' 
                AND datetime(updated_at) < datetime('now', '-2 hours')
                ORDER BY updated_at ASC
            """)
            
            stuck_matches = result.rows if result.rows else []
            
            if not stuck_matches:
                logger.info("✅ Nenhuma partida travada encontrada")
                return
            
            logger.warning(f"⚠️  {len(stuck_matches)} partida(s) travada(s) detectada(s)")
            
            # Para cada partida travada, verificar na API
            for stuck in stuck_matches:
                match_id = stuck[1]  # match_id
                old_updated = stuck[3]  # updated_at
                
                logger.info(f"   🔄 Verificando partida ID {match_id} (última atualização: {old_updated})")
                
                try:
                    # Buscar na API usando endpoint /past (finished matches)
                    finished = await self.api_client.get_past_matches(per_page=100)
                    
                    # Procurar a partida em finished
                    for match in finished:
                        if match.get('id') == match_id:
                            logger.warning(f"      🔴 Partida {match_id} mudou de RUNNING → FINISHED")
                            logger.warning(f"         Status na API: {match.get('status')}")
                            logger.warning(f"         Resultado: {match.get('results', [])}")
                            
                            # Atualizar no cache
                            await self.cache_manager.cache_matches([match], "detection")
                            logger.info(f"      ✅ Partida {match_id} atualizada para FINISHED")
                            break
                    else:
                        # Não encontrou em finished, tentar buscar direto
                        logger.info(f"      ℹ️  Partida {match_id} não está em finished, tentando busca direta...")
                        
                        # Buscar status atual na API
                        all_matches = await self.api_client.get_matches(per_page=1)
                        if all_matches:
                            current_status = all_matches[0].get('status')
                            if current_status != 'running':
                                logger.warning(f"      🔄 Status mudou de RUNNING → {current_status}")
                                await self.cache_manager.cache_matches(all_matches, "detection")
                                logger.info(f"      ✅ Partida {match_id} atualizada para {current_status}")
                            else:
                                logger.info(f"      ⏳ Partida {match_id} ainda em RUNNING (pode estar travada)")
                
                except Exception as e:
                    logger.error(f"      ✗ Erro ao verificar partida {match_id}: {e}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao detectar partidas travadas: {e}")
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
