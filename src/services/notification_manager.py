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
            
            if not match_id or not begin_at:
                logger.warning(f"Partida incompleta: id={match_id}, begin_at={begin_at}")
                return False
            
            # Converter string ISO para datetime
            if isinstance(begin_at, str):
                match_time = datetime.fromisoformat(begin_at.replace('Z', '+00:00')).replace(tzinfo=None)
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
        for match in matches:
            if await self.setup_reminders_for_match(guild_id, match):
                count += 1
        
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
            
            # Buscar TODOS os lembretes pendentes (não só os vencidos)
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
            
            # Log de status geral
            if all_reminders:
                logger.debug(f"⏰ VERIFICAÇÃO DE LEMBRETES | Total pendentes: {len(all_reminders)} | Hora: {now.strftime('%H:%M:%S')}")
            
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
                
                # Mostrar quanto tempo falta
                if time_until.total_seconds() > 0:
                    remaining_minutes = int(time_until.total_seconds() / 60)
                    remaining_seconds = int(time_until.total_seconds() % 60)
                    logger.debug(f"  ⏳ Partida {match_id} ({minutes_before}min): Faltam {remaining_minutes}m {remaining_seconds}s")
                
                # Enviar apenas se já venceu
                if scheduled_time <= now:
                    logger.info(f"  🚀 ENVIANDO: Partida {match_id} - Lembrete de {minutes_before} minutos")
                    
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
                            logger.info(f"  ✅ Marcado como enviado: Partida {match_id} ({minutes_before}min)")
                        except Exception as e:
                            logger.error(f"  ❌ Erro ao marcar lembrete como enviado: {e}")
                    else:
                        logger.warning(f"  ⚠️ Falha ao enviar: Partida {match_id} ({minutes_before}min)")
            
            if sent_count > 0:
                logger.info(f"✅ Ciclo de lembretes concluído: {sent_count} enviados")
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes pendentes: {e}")
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
            
            logger.debug(f"[NOTIF] Iniciando envio para guild {guild_id}, partida {match_id}")
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.error(f"[NOTIF] ❌ Guild {guild_id} não encontrada no bot")
                return False
            
            logger.debug(f"[NOTIF] ✅ Guild encontrada: {guild.name}")
            
            # Buscar canal de notificações
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT notification_channel_id FROM guild_config WHERE guild_id = ?",
                [guild_id]
            )
            
            if not result.rows:
                logger.warning(f"[NOTIF] ⚠️ Guild {guild_id} não tem configuração no banco")
                return False
            
            channel_id = result.rows[0][0]
            if not channel_id:
                logger.warning(f"[NOTIF] ⚠️ Guild {guild_id} não tem canal de notificações configurado")
                return False
            
            logger.debug(f"[NOTIF] Canal ID encontrado: {channel_id}")
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"[NOTIF] ❌ Canal {channel_id} não encontrado no bot")
                return False
            
            logger.debug(f"[NOTIF] ✅ Canal encontrado: #{channel.name}")
            
            # Parsear dados da partida
            match = json.loads(match_data)
            
            # Criar embed de notificação
            embed = self._create_reminder_embed(match, minutes_before)
            
            # Enviar mensagem
            message = await channel.send(embed=embed)
            logger.info(f"[NOTIF] ✅ ENVIADA: Guild {guild_id} | Partida {match_id} | {minutes_before}min | MSG ID: {message.id}")
            return True
            
        except Exception as e:
            logger.error(f"[NOTIF] ❌ Erro ao enviar notificação: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _create_reminder_embed(self, match: Dict, minutes_before: int) -> nextcord.Embed:
        """Cria um embed para notificação de lembrete."""
        
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
        
        begin_at = match.get('begin_at', 'Horário não disponível')
        embed.add_field(name="⏰ Horário", value=str(begin_at), inline=False)
        
        embed.set_footer(text="Bot HLTV - Notificações de Partidas")
        
        return embed
    
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
        """Loop que verifica lembretes a cada minuto."""
        logger.debug(f"🔍 Verificando lembretes pendentes...")
        await self.send_pending_reminders()
    
    @_reminder_loop.before_loop
    async def before_reminder_loop(self):
        """Aguarda o bot ficar pronto antes de iniciar."""
        await self.bot.wait_until_ready()
        logger.info("✅ Bot pronto | Verificação de lembretes ATIVA")
