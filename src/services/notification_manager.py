"""
Gerenciador de notificações e lembretes de partidas.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from nextcord.ext import tasks
import nextcord

from src.database.cache_manager import MatchCacheManager

logger = logging.getLogger(__name__)


class NotificationManager:
    """Gerencia notificações e lembretes de partidas."""
    
    # Minutos antes do início da partida para enviar lembretes
    REMINDER_TIMES = [60, 30, 15, 5, 0]  # 1h, 30min, 15min, 5min, em tempo real
    
    def __init__(self, bot: "nextcord.ext.commands.Bot", cache_manager: MatchCacheManager):
        """
        Inicializa o gerenciador de notificações.
        
        Args:
            bot: Instância do bot
            cache_manager: Gerenciador de cache de partidas
        """
        self.bot = bot
        self.cache_manager = cache_manager
        self.is_running = False
        
        logger.info("📬 NotificationManager inicializado")
    
    async def setup_reminders_for_match(self, guild_id: int, match: Dict) -> bool:
        """
        Cria lembretes para uma partida específica.
        
        Args:
            guild_id: ID do servidor Discord
            match: Dados da partida
            
        Returns:
            bool: True se agendado com sucesso
        """
        try:
            match_id = match.get('id')
            begin_at = match.get('begin_at')
            status = match.get('status')
            
            # Verificar se partida tem dados completos e está no futuro
            if not match_id:
                logger.debug(f"⏭️ Partida sem ID: Pulada")
                return False
            
            # Só agendar partidas futuras (not_started ou running)
            if status not in ['not_started', 'running']:
                logger.debug(f"⏭️ Partida {match_id}: Status '{status}' - Pulada (não é futura)")
                return False
            
            if not begin_at:
                logger.debug(f"⏭️ Partida {match_id}: Sem begin_at - Pulada")
                return False
            
            # Converter string ISO para datetime
            if isinstance(begin_at, str):
                from datetime import timezone
                # Parse com timezone UTC
                match_time_utc = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
                # Converter para hora local
                match_time = match_time_utc.astimezone().replace(tzinfo=None)
            else:
                match_time = begin_at
            
            # Verificar se a partida ainda não começou
            now = datetime.now()
            if match_time < now:
                logger.debug(f"Partida {match_id} já começou, ignorando")
                return False
            
            time_until_match = match_time - now
            logger.info(f"📅 Partida {match_id}: Começa em {time_until_match}")
            
            client = await self.cache_manager.get_client()
            
            # Criar lembretes para cada intervalo
            scheduled_count = 0
            for minutes_before in self.REMINDER_TIMES:
                scheduled_time = match_time - timedelta(minutes=minutes_before)
                
                # Só agendar se for no futuro
                if scheduled_time < now:
                    logger.debug(f"  ⏭️ Lembrete de {minutes_before}min já passou para partida {match_id}")
                    continue
                
                try:
                    # Tentar inserir (ignorar se já existe)
                    await client.execute(
                        """
                        INSERT INTO match_reminders 
                        (guild_id, match_id, reminder_minutes_before, scheduled_time, sent)
                        VALUES (?, ?, ?, ?, 0)
                        ON CONFLICT(guild_id, match_id, reminder_minutes_before) DO NOTHING
                        """,
                        [guild_id, match_id, minutes_before, scheduled_time.isoformat()]
                    )
                    
                    time_until_reminder = scheduled_time - now
                    logger.info(f"  ✅ Agendado: {minutes_before}min ANTES | Lembrete em: {time_until_reminder}")
                    scheduled_count += 1
                    
                except Exception as e:
                    logger.error(f"  ❌ Erro ao agendar lembrete de {minutes_before}min: {e}")
                    continue
            
            logger.info(f"✓ Partida {match_id}: {scheduled_count} lembretes agendados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao preparar lembretes para partida: {e}")
            return False
    
    async def setup_reminders_for_all_matches(self, guild_id: int, matches: List[Dict]) -> int:
        """
        Cria lembretes para múltiplas partidas.
        
        Args:
            guild_id: ID do servidor Discord
            matches: Lista de partidas
            
        Returns:
            int: Número de partidas com lembretes agendados
        """
        count = 0
        skipped_no_status = 0
        skipped_old_status = 0
        skipped_no_begin = 0
        
        logger.info(f"📋 Filtrando {len(matches)} partidas para agendamento...")
        
        for match in matches:
            status = match.get('status')
            begin_at = match.get('begin_at')
            match_id = match.get('id')
            
            # Verificar status primeiro
            if status not in ['not_started', 'running']:
                skipped_old_status += 1
                continue
            
            # Verificar begin_at
            if not begin_at:
                skipped_no_begin += 1
                continue
            
            if await self.setup_reminders_for_match(guild_id, match):
                count += 1
        
        # Log de resumo
        logger.info(f"✅ Resultado da filtragem:")
        logger.info(f"   ✓ {count} partidas agendadas")
        if skipped_old_status > 0:
            logger.info(f"   ⏭️ {skipped_old_status} partidas puladas (status finished/canceled)")
        if skipped_no_begin > 0:
            logger.info(f"   ⏭️ {skipped_no_begin} partidas puladas (sem begin_at)")
        
        logger.info(f"✓ {count} partidas com lembretes agendados para guild {guild_id}")
        return count
    
    async def send_pending_reminders(self) -> int:
        """
        Envia lembretes pendentes.
        
        Returns:
            int: Número de lembretes enviados
        """
        try:
            client = await self.cache_manager.get_client()
            now = datetime.now()
            now_str = now.strftime('%H:%M:%S')
            
            # Buscar TODOS os lembretes pendentes
            result = await client.execute(
                """
                SELECT mr.id, mr.guild_id, mr.match_id, mr.reminder_minutes_before,
                       mr.scheduled_time, mc.match_data
                FROM match_reminders mr
                JOIN matches_cache mc ON mr.match_id = mc.match_id
                WHERE mr.sent = 0
                ORDER BY mr.scheduled_time ASC
                """,
                []
            )
            
            all_reminders = result.rows if result.rows else []
            sent_count = 0
            vencidos = 0
            pendentes = 0
            
            # Log inicial
            logger.info(f"   📊 Total de lembretes pendentes (não enviados): {len(all_reminders)}")
            
            if not all_reminders:
                logger.info(f"   ✅ Nenhum lembrete pendente no banco de dados")
                return 0
            
            for reminder in all_reminders:
                reminder_id = reminder[0]
                guild_id = reminder[1]
                match_id = reminder[2]
                minutes_before = reminder[3]
                scheduled_time_str = reminder[4]
                match_data = reminder[5]
                
                # Converter scheduled_time para datetime
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
                time_until = scheduled_time - now
                total_seconds = time_until.total_seconds()
                
                # Verificar se já venceu
                if total_seconds <= 0:
                    vencidos += 1
                    logger.info(f"   🚀 ENVIANDO AGORA: Match {match_id} | {minutes_before}min antes | Vencido há {abs(int(total_seconds))}s")
                    
                    # Enviar notificação
                    if await self._send_reminder_notification(guild_id, match_id, match_data, minutes_before):
                        # Marcar como enviado
                        try:
                            await client.execute(
                                """
                                UPDATE match_reminders 
                                SET sent = 1, sent_at = ?
                                WHERE id = ?
                                """,
                                [now.isoformat(), reminder_id]
                            )
                            sent_count += 1
                            logger.info(f"      ✅ Sucesso: Lembrete marcado como enviado (ID: {reminder_id})")
                        except Exception as e:
                            logger.error(f"      ❌ Erro ao marcar como enviado: {e}")
                    else:
                        logger.warning(f"      ⚠️ Falha ao enviar notificação")
                else:
                    # Ainda não venceu
                    pendentes += 1
                    remaining_minutes = int(total_seconds / 60)
                    remaining_seconds = int(total_seconds % 60)
                    logger.info(f"   ⏳ Aguardando: Match {match_id} | {minutes_before}min | Falta {remaining_minutes}m {remaining_seconds}s")
            
            # Log final detalhado
            logger.info(f"   📈 RESUMO: {vencidos} vencidos, {pendentes} ainda pendentes, {sent_count} enviados")
            
            return sent_count
            
        except Exception as e:
            logger.error(f"❌ ERRO em send_pending_reminders: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    async def _send_reminder_notification(
        self, 
        guild_id: int, 
        match_id: int, 
        match_data: str,
        minutes_before: int
    ) -> bool:
        """
        Envia uma notificação de lembrete.
        
        Args:
            guild_id: ID do servidor
            match_id: ID da partida
            match_data: JSON da partida
            minutes_before: Quantos minutos antes do início
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            import json
            
            logger.info(f"      [NOTIF-INIT] Iniciando envio para guild {guild_id}, match {match_id}")
            
            # 1. Verificar se guild existe
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.error(f"      [NOTIF-ERR] ❌ Guild {guild_id} NÃO encontrada no bot")
                return False
            
            logger.info(f"      [NOTIF-OK] ✅ Guild encontrada: '{guild.name}' (ID: {guild_id})")
            
            # 2. Buscar configuração da guild (incluindo timezone)
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT notification_channel_id, timezone FROM guild_config WHERE guild_id = ?",
                [guild_id]
            )
            
            if not result.rows:
                logger.error(f"      [NOTIF-ERR] ❌ Guild {guild_id} SEM configuração no banco")
                return False
            
            channel_id = result.rows[0][0]
            timezone = result.rows[0][1] or "America/Sao_Paulo"
            
            # 3. Verificar se channel_id foi configurado
            if not channel_id:
                logger.error(f"      [NOTIF-ERR] ❌ Guild {guild_id} SEM canal de notificações configurado")
                return False
            
            logger.info(f"      [NOTIF-OK] ✅ Canal ID encontrado: {channel_id}")
            
            # 4. Buscar o canal no bot
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"      [NOTIF-ERR] ❌ Canal {channel_id} NÃO encontrado no bot")
                return False
            
            logger.info(f"      [NOTIF-OK] ✅ Canal encontrado: #{channel.name}")
            
            # 5. Parsear dados da partida
            try:
                match = json.loads(match_data)
                logger.info(f"      [NOTIF-OK] ✅ Dados da partida parseados")
            except Exception as e:
                logger.error(f"      [NOTIF-ERR] ❌ Erro ao fazer parse do JSON: {e}")
                return False
            
            # 6. Criar embed
            # Converter timezone para string (libSQL retorna bytes)
            tz_str = timezone.decode() if isinstance(timezone, bytes) else str(timezone or "America/Sao_Paulo")
            embed = await self._create_reminder_embed(match, minutes_before, timezone=tz_str)
            logger.info(f"      [NOTIF-OK] ✅ Embed criado")
            
            # 7. Enviar mensagem
            try:
                message = await channel.send(embed=embed)
                logger.info(f"      [NOTIF-SUCCESS] ✅ ENVIADA COM SUCESSO!")
                logger.info(f"         Guild: {guild.name} ({guild_id})")
                logger.info(f"         Canal: #{channel.name} ({channel_id})")
                logger.info(f"         Partida: {match_id}")
                logger.info(f"         Lembrete: {minutes_before} minutos antes")
                logger.info(f"         MSG ID: {message.id}")
                return True
            except Exception as e:
                logger.error(f"      [NOTIF-ERR] ❌ Erro ao enviar no Discord: {type(e).__name__}: {e}")
                return False
            
        except Exception as e:
            logger.error(f"      [NOTIF-FATAL] ❌ ERRO FATAL: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def _create_reminder_embed(self, match: Dict, minutes_before: int, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
        """Cria um embed para notificação de lembrete com informações de streams."""
        
        from src.utils.timezone_manager import TimezoneManager
        
        # Definir texto do lembrete
        if minutes_before == 0:
            reminder_text = "🔴 **A PARTIDA ESTÁ COMEÇANDO AGORA!**"
            color = nextcord.Color.red()
        elif minutes_before == 5:
            reminder_text = "🟡 **PARTIDA COMEÇANDO EM 5 MINUTOS!**"
            color = nextcord.Color.orange()
        elif minutes_before == 15:
            reminder_text = "🟠 Partida começando em 15 minutos"
            color = nextcord.Color.gold()
        elif minutes_before == 30:
            reminder_text = "🟡 Partida começando em 30 minutos"
            color = nextcord.Color.yellow()
        else:  # 60
            reminder_text = "🔔 Partida começando em 1 hora"
            color = nextcord.Color.blue()
        
        # Extrair informações
        team1 = match.get('opponents', [{}])[0]
        team2 = match.get('opponents', [{}])[1] if len(match.get('opponents', [])) > 1 else {}
        
        team1_name = team1.get('opponent', {}).get('name', 'Time 1') if team1.get('opponent') else 'Time 1'
        team2_name = team2.get('opponent', {}).get('name', 'Time 2') if team2.get('opponent') else 'Time 2'
        
        tournament = match.get('league', {}).get('name', 'Torneio desconhecido') if match.get('league') else 'Torneio desconhecido'
        
        embed = nextcord.Embed(
            title=reminder_text,
            description=f"{team1_name} **vs** {team2_name}",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📅 Torneio", value=tournament, inline=False)
        
        # ✨ Usar TimezoneManager para horário com timezone
        begin_at = match.get('begin_at', 'Horário não disponível')
        if begin_at and isinstance(begin_at, str):
            try:
                dt_utc = TimezoneManager.parse_iso_datetime(begin_at)
                timestamp_discord = TimezoneManager.discord_timestamp(dt_utc, timezone, format_type="f")
                tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
                tz_offset = TimezoneManager.get_timezone_offset(timezone)
                horario_display = f"{timestamp_discord} ({tz_abbr} {tz_offset})"
            except Exception as e:
                horario_display = str(begin_at)
        else:
            horario_display = str(begin_at)
        
        embed.add_field(name="⏰ Horário", value=horario_display, inline=False)
        
        # NOVO: Adicionar streams se disponíveis
        try:
            match_id = match.get("id")
            if match_id:
                from src.utils.embeds import format_streams_field
                streams = await self.cache_manager.get_match_streams(match_id)
                if streams:
                    formatted_streams = format_streams_field(streams)
                    if formatted_streams:
                        embed.add_field(
                            name="📡 Streams",
                            value=formatted_streams,
                            inline=False
                        )
        except Exception as e:
            logger.debug(f"Erro ao adicionar streams ao lembrete: {e}")
        
        embed.set_footer(text="Bot HLTV - Notificações de Partidas")
        
        return embed
    
    async def schedule_result_notification(self, guild_id: int, match_id: int) -> bool:
        """
        Agenda uma notificação de RESULTADO para ser enviada IMEDIATAMENTE.
        
        Args:
            guild_id: ID do servidor Discord
            match_id: ID da partida
            
        Returns:
            bool: True se agendado com sucesso
        """
        try:
            client = await self.cache_manager.get_client()
            now = datetime.now()
            
            # Inserir com scheduled_time = AGORA (para envio rápido)
            await client.execute(
                """
                INSERT INTO match_result_notifications
                (guild_id, match_id, scheduled_time, sent)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(guild_id, match_id) DO UPDATE SET
                    scheduled_time = excluded.scheduled_time,
                    sent = 0
                """,
                [guild_id, match_id, now.isoformat()]
            )
            
            logger.info(f"📬 Resultado agendado: Guild {guild_id}, Match {match_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao agendar resultado: {e}")
            return False
    
    async def send_pending_result_notifications(self) -> int:
        """
        Envia notificações de RESULTADO pendentes.
        Similar a send_pending_reminders mas para resultados.
        
        Returns:
            int: Número de notificações enviadas
        """
        try:
            client = await self.cache_manager.get_client()
            now = datetime.now()
            
            # Buscar notificações de resultado pendentes
            result = await client.execute(
                """
                SELECT mrn.id, mrn.guild_id, mrn.match_id,
                       mrn.scheduled_time, mc.match_data
                FROM match_result_notifications mrn
                JOIN matches_cache mc ON mrn.match_id = mc.match_id
                WHERE mrn.sent = 0
                AND datetime(mrn.scheduled_time) <= datetime(?)
                ORDER BY mrn.scheduled_time ASC
                """,
                [now.isoformat()]
            )
            
            result_notifications = result.rows if result.rows else []
            sent_count = 0
            
            logger.info(f"   📊 {len(result_notifications)} notificação(ões) de resultado pendente(s)")
            
            if not result_notifications:
                logger.debug(f"   ✅ Nenhuma notificação de resultado para enviar")
                return 0
            
            for notification in result_notifications:
                notif_id = notification[0]
                guild_id = notification[1]
                match_id = notification[2]
                scheduled_time_str = notification[3]
                match_data = notification[4]
                
                logger.info(f"   🚀 ENVIANDO RESULTADO: Match {match_id} para Guild {guild_id}")
                
                # Enviar notificação
                if await self._send_result_notification(guild_id, match_id, match_data):
                    # Marcar como enviado
                    try:
                        await client.execute(
                            """
                            UPDATE match_result_notifications
                            SET sent = 1, sent_at = ?
                            WHERE id = ?
                            """,
                            [now.isoformat(), notif_id]
                        )
                        sent_count += 1
                        logger.info(f"      ✅ Resultado marcado como enviado")
                    except Exception as e:
                        logger.error(f"      ❌ Erro ao marcar como enviado: {e}")
                else:
                    logger.warning(f"      ⚠️ Falha ao enviar resultado")
            
            logger.info(f"   📈 Total de resultados enviados: {sent_count}")
            return sent_count
            
        except Exception as e:
            logger.error(f"❌ ERRO em send_pending_result_notifications: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    async def _send_result_notification(
        self,
        guild_id: int,
        match_id: int,
        match_data: str
    ) -> bool:
        """
        Envia uma notificação de RESULTADO para Discord.
        
        Args:
            guild_id: ID do servidor
            match_id: ID da partida
            match_data: JSON da partida com resultado
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            import json
            from src.utils.embeds import create_result_embed
            
            logger.info(f"      [RESULT-INIT] Iniciando envio para guild {guild_id}, match {match_id}")
            
            # 1. Verificar se guild existe
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.error(f"      [RESULT-ERR] ❌ Guild {guild_id} NÃO encontrada")
                return False
            
            logger.info(f"      [RESULT-OK] ✅ Guild encontrada: '{guild.name}'")
            
            # 2. Buscar configuração da guild (incluindo timezone)
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT notification_channel_id, timezone FROM guild_config WHERE guild_id = ?",
                [guild_id]
            )
            
            if not result.rows:
                logger.error(f"      [RESULT-ERR] ❌ Guild {guild_id} SEM configuração")
                return False
            
            channel_id = result.rows[0][0]
            timezone = result.rows[0][1] or "America/Sao_Paulo"
            
            # 3. Verificar se channel_id foi configurado
            if not channel_id:
                logger.error(f"      [RESULT-ERR] ❌ Guild {guild_id} SEM canal configurado")
                return False
            
            logger.info(f"      [RESULT-OK] ✅ Canal ID: {channel_id}")
            
            # 4. Buscar o canal
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"      [RESULT-ERR] ❌ Canal {channel_id} NÃO encontrado")
                return False
            
            logger.info(f"      [RESULT-OK] ✅ Canal: #{channel.name}")
            
            # 5. Parsear dados da partida
            try:
                match = json.loads(match_data)
                logger.info(f"      [RESULT-OK] ✅ Dados parseados")
            except Exception as e:
                logger.error(f"      [RESULT-ERR] ❌ Erro ao parsear JSON: {e}")
                return False
            
            # 6. Criar embed de resultado com timezone
            # Converter timezone para string (libSQL retorna bytes)
            tz_str = timezone.decode() if isinstance(timezone, bytes) else str(timezone or "America/Sao_Paulo")
            embed = create_result_embed(match, timezone=tz_str)
            
            # NOVO: Adicionar streams se disponíveis
            try:
                match_id = match.get("id")
                if match_id:
                    from src.utils.embeds import format_streams_field
                    streams = await self.cache_manager.get_match_streams(match_id)
                    if streams:
                        formatted_streams = format_streams_field(streams)
                        if formatted_streams:
                            embed.add_field(
                                name="📡 Streams",
                                value=formatted_streams,
                                inline=False
                            )
            except Exception as e:
                logger.debug(f"Erro ao adicionar streams à notificação de resultado: {e}")
            
            logger.info(f"      [RESULT-OK] ✅ Embed criado")
            
            # 7. Enviar mensagem
            try:
                message = await channel.send(embed=embed)
                logger.info(f"      [RESULT-SUCCESS] ✅ ENVIADA COM SUCESSO!")
                logger.info(f"         Guild: {guild.name} ({guild_id})")
                logger.info(f"         Canal: #{channel.name} ({channel_id})")
                logger.info(f"         Partida: {match_id}")
                logger.info(f"         MSG ID: {message.id}")
                return True
            except Exception as e:
                logger.error(f"      [RESULT-ERR] ❌ Erro ao enviar: {type(e).__name__}: {e}")
                return False
            
        except Exception as e:
            logger.error(f"      [RESULT-FATAL] ❌ ERRO FATAL: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def start_reminder_loop(self):
        """Inicia o loop de verificação de lembretes."""
        if not self.is_running:
            self.is_running = True
            self._reminder_loop.start()
            logger.info("🔄 Loop de lembretes INICIADO | Verificando a cada 1 minuto")
    
    def stop_reminder_loop(self):
        """Para o loop de verificação de lembretes."""
        if self.is_running:
            self.is_running = False
            self._reminder_loop.stop()
            logger.info("⏹️ Loop de lembretes PARADO")
    
    @tasks.loop(minutes=1)
    async def _reminder_loop(self):
        """Loop que verifica lembretes e resultados a cada minuto."""
        now = datetime.now().strftime('%H:%M:%S')
        logger.info(f"🔍 [VERIFICAÇÃO] Checando notificações - {now}")
        
        # Enviar lembretes de INÍCIO
        count_reminders = await self.send_pending_reminders()
        
        # ⭐ NOVO: Enviar notificações de RESULTADO
        count_results = await self.send_pending_result_notifications()
        
        if count_reminders == 0 and count_results == 0:
            logger.info(f"   ℹ️ Nenhuma notificação neste momento")
        
        logger.info(f"✅ [VERIFICAÇÃO CONCLUÍDA] {now}")
    
    @_reminder_loop.before_loop
    async def before_reminder_loop(self):
        """Aguarda o bot ficar pronto antes de iniciar."""
        await self.bot.wait_until_ready()
        logger.info("✅ Bot pronto | Verificação de lembretes ATIVA")
