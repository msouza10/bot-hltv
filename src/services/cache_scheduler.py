"""
Agendador para atualização periódica do cache usando Discord Tasks.
"""

import asyncio
import logging
from datetime import datetime, timezone
from nextcord.ext import tasks

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager

logger = logging.getLogger(__name__)

# Lock para evitar race conditions entre tasks
_cache_update_lock = asyncio.Lock()


def format_timestamp_with_tz(timestamp_str):
    """
    Problema 8: Melhorar timestamp logging com informação de timezone.
    Converte timestamp para formato legível com timezone info.
    """
    try:
        if not timestamp_str:
            return "N/A"
        
        # Se for string, tentar fazer parse
        if isinstance(timestamp_str, str):
            # Assumir UTC se não tiver timezone info
            if '+' not in timestamp_str and 'Z' not in timestamp_str:
                timestamp_str += 'Z'
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = timestamp_str
        
        # Formatação com timezone
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z (UTC)")
    except Exception:
        return str(timestamp_str)


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
        """
        Atualiza todas as partidas (upcoming, running, past e canceladas).
        Usa lock para evitar overlaps com update_live_matches.
        """
        # Evitar race condition com update_live_matches
        async with _cache_update_lock:
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
        Detecta se alguma partida mudou de status e atualiza o cache.
        
        LÓGICA CORRIGIDA:
        - Se partida estava RUNNING no cache mas não está em all_matches atualizado
        - Significa que MUDOU DE STATUS (saiu de running)
        - Procura em all_matches para confirmar novo status
        """
        try:
            # Extrair IDs das partidas atuais
            current_ids = {match.get('id'): match for match in all_matches}
            
            # Buscar partidas em cache que estão com status 'running'
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT match_id, status FROM matches_cache WHERE status = 'running' AND updated_at > datetime('now', '-7 days')"
            )
            
            cached_running = {row[0]: row[1] for row in (result.rows or [])}
            
            # Comparar: partidas que estavam RUNNING mas saíram da lista
            missing_ids = set()
            for match_id in cached_running.keys():
                if match_id not in current_ids:
                    missing_ids.add(match_id)
            
            if not missing_ids:
                logger.debug("✅ Nenhuma transição de estado na validação completa")
                return
            
            logger.warning(f"🔄 {len(missing_ids)} partida(s) não encontrada na atualização (possível mudança de estado)")
            
            # Para cada partida desaparecida, procurar novo status em all_matches
            # Ela pode estar com status diferente agora (finished, canceled, etc)
            for match_id in missing_ids:
                logger.info(f"   🔍 Procurando partida {match_id} em finished/canceled...")
                
                try:
                    # Buscar em finished
                    finished = await self.api_client.get_past_matches(hours=24, per_page=100)
                    
                    found = False
                    for match in finished:
                        if match.get('id') == match_id:
                            old_status = cached_running[match_id]
                            new_status = match.get('status')
                            
                            logger.warning(f"      🔴 TRANSIÇÃO: {old_status} → {new_status}")
                            logger.warning(f"         Match: {match.get('name')}")
                            logger.warning(f"         Resultado: {match.get('results', [])}")
                            
                            # Atualizar no cache
                            await self.cache_manager.cache_matches([match], "state_transition")
                            logger.info(f"      ✅ Cache atualizado!")
                            found = True
                            break
                    
                    if not found:
                        logger.warning(f"      ⚠️  Partida {match_id} não encontrada em finished")
                        logger.info(f"         (Pode estar com status diferente ou removida da API)")
                
                except Exception as e:
                    logger.error(f"      ✗ Erro ao validar transição: {e}")
        
        except Exception as e:
            logger.error(f"✗ Erro ao validar transições de estado: {e}")
            import traceback
            traceback.print_exc()
    
    async def update_live_matches(self):
        """
        Atualiza apenas partidas ao vivo (mais frequente).
        Usa lock para evitar overlaps com update_all_matches.
        """
        # Evitar race condition com update_all_matches
        async with _cache_update_lock:
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
        
        LÓGICA CORRIGIDA:
        - cached_running: IDs em RUNNING no cache
        - running_now: IDs em RUNNING na API AGORA
        - transitions: cached_running - running_now (saíram de running)
        - Confirma se estão em finished
        """
        try:
            if not running_matches:
                return
            
            # IDs que estão RUNNING na API agora
            running_ids_now = {m.get('id') for m in running_matches}
            
            # Buscar partidas finished recentes (últimas 2h)
            finished = await self.api_client.get_past_matches(hours=2, per_page=50)
            finished_dict = {m.get('id'): m for m in finished}
            
            # Buscar IDs que estão RUNNING no cache
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT match_id FROM matches_cache WHERE status = 'running' AND updated_at > datetime('now', '-7 days')"
            )
            cached_running_ids = {row[0] for row in (result.rows or [])}
            
            # TRANSIÇÃO: Partidas que estavam running mas saíram (não estão mais na API running)
            # E agora estão em finished
            transitioned_ids = []
            for match_id in cached_running_ids:
                if match_id not in running_ids_now and match_id in finished_dict:
                    transitioned_ids.append(match_id)
            
            if not transitioned_ids:
                logger.debug("✅ Nenhuma transição running→finished detectada")
                return
            
            logger.warning(f"🔥 {len(transitioned_ids)} partida(s) mudou de RUNNING → FINISHED")
            
            # Atualizar todas as transições
            for match_id in transitioned_ids:
                finished_match = finished_dict[match_id]
                logger.warning(f"   🔴 {finished_match.get('name')}")
                logger.warning(f"      ID: {match_id}")
                logger.warning(f"      Status: {finished_match.get('status')}")
                logger.warning(f"      Resultado: {finished_match.get('results', [])}")
                
                # Atualizar no cache
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
        
        OTIMIZAÇÕES:
        - Busca finished UMA VEZ (não para cada partida)
        - Filtra partidas antigas (> 7 dias)
        - Try-finally garante que resources sejam liberados
        - Idempotente: Lock garante execução exclusiva
        """
        client = None
        try:
            logger.info("🔍 Verificando se há partidas travadas (running há 2+ horas)...")
            
            # Buscar partidas running há mais de 2 horas
            client = await self.cache_manager.get_client()
            result = await client.execute("""
                SELECT id, match_id, begin_at, updated_at 
                FROM matches_cache 
                WHERE status = 'running' 
                AND datetime(updated_at) < datetime('now', '-2 hours')
                AND updated_at > datetime('now', '-7 days')
                ORDER BY updated_at ASC
            """)
            
            stuck_matches = result.rows if result.rows else []
            
            if not stuck_matches:
                logger.debug("✅ Nenhuma partida travada encontrada")
                return
            
            logger.warning(f"⚠️  {len(stuck_matches)} partida(s) travada(s) detectada(s)")
            
            # 🔥 OTIMIZAÇÃO: Buscar finished UMA VEZ para todas
            finished = await self.api_client.get_past_matches(hours=24, per_page=100)
            finished_dict = {m.get('id'): m for m in finished}
            
            if not finished_dict:
                logger.warning("⚠️  API não retornou partidas finished para validar")
                return
            
            # Procurar cada partida travada em finished
            for stuck in stuck_matches:
                match_id = stuck[1]  # match_id
                old_updated = stuck[3]  # updated_at
                
                # Problema 8: Usar format_timestamp_with_tz para melhor legibilidade
                formatted_time = format_timestamp_with_tz(old_updated)
                logger.info(f"   🔄 Verificando partida ID {match_id} (última atualização: {formatted_time})")
                
                try:
                    if match_id in finished_dict:
                        # Encontrou em finished!
                        match = finished_dict[match_id]
                        logger.warning(f"      🔴 Partida {match_id} mudou de RUNNING → FINISHED")
                        logger.warning(f"         Status na API: {match.get('status')}")
                        logger.warning(f"         Resultado: {match.get('results', [])}")
                        
                        # Atualizar no cache
                        await self.cache_manager.cache_matches([match], "stuck_detection")
                        logger.info(f"      ✅ Partida {match_id} atualizada para FINISHED")
                    else:
                        # Não está em finished, pode estar ainda running ou cancelada
                        logger.warning(f"      ⏳ Partida {match_id} AINDA está em RUNNING (possível travamento real)")
                        logger.warning(f"         Última atualização: {formatted_time}")
                        logger.warning(f"         Ação: Aguardando próxima verificação")
                
                except Exception as e:
                    logger.error(f"      ✗ Erro ao verificar partida {match_id}: {e}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao detectar partidas travadas: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Problema 7: Garantir limpeza de recursos
            if client:
                try:
                    # Liberar conexão se necessário
                    logger.debug("🔧 Liberando recursos do cliente de cache")
                except Exception as e:
                    logger.error(f"✗ Erro ao liberar recursos: {e}")
    
    # Task: Atualização completa a cada 15 minutos
    @tasks.loop(minutes=15, count=None)
    async def update_all_task(self):
        """Task do Discord para atualização completa."""
        await self.update_all_matches()
    
    # Task: Atualização de partidas ao vivo a cada 5 minutos
    @tasks.loop(minutes=5, count=None)
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
