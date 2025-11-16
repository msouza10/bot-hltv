"""
Cog para comandos de configuração de notificações de partidas.
"""

import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging

logger = logging.getLogger(__name__)


class NotificationsCog(commands.Cog):
    """Comandos para configurar notificações de partidas."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(
        name="notificacoes",
        description="Ativa/desativa notificações de partidas no servidor"
    )
    async def notificacoes(
        self,
        interaction: nextcord.Interaction,
        ativar: bool = SlashOption(
            name="ativar",
            description="Ativar ou desativar notificações",
            required=True
        )
    ):
        """Ativa ou desativa notificações de partidas."""
        
        # Verificar permissões
        if not interaction.user.guild_permissions.administrator:
            embed = nextcord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem configurar notificações.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        
        try:
            client = await self.bot.cache_manager.get_client()
            
            # Garantir que existe registro de configuração
            await client.execute(
                """
                INSERT OR IGNORE INTO guild_config (guild_id, notify_upcoming, notify_live)
                VALUES (?, 1, 1)
                """,
                [guild_id]
            )
            
            # Atualizar configuração
            await client.execute(
                """
                UPDATE guild_config 
                SET notify_upcoming = ?, notify_live = ?
                WHERE guild_id = ?
                """,
                [1 if ativar else 0, 1 if ativar else 0, guild_id]
            )
            
            status = "✅ **Ativadas**" if ativar else "❌ **Desativadas**"
            
            embed = nextcord.Embed(
                title="Notificações",
                description=f"Notificações de partidas agora estão {status}",
                color=nextcord.Color.green() if ativar else nextcord.Color.red()
            )
            
            if ativar:
                # Agendar lembretes para todas as partidas no cache
                matches = await self.bot.cache_manager.get_cached_matches_fast("not_started", limit=50)
                
                logger.info(f"📋 Comando /notificacoes ativar:true em guild {guild_id}")
                logger.info(f"   📊 Total de partidas em cache: {len(matches) if matches else 0}")
                
                if matches:
                    logger.info(f"   🚀 Iniciando agendamento de lembretes...")
                    scheduled_count = await self.bot.notification_manager.setup_reminders_for_all_matches(
                        guild_id, 
                        matches
                    )
                    embed.add_field(
                        name=f"📬 {scheduled_count} partidas agendadas",
                        value="Lembretes em: 1h, 30min, 15min, 5min e ao vivo",
                        inline=False
                    )
                    logger.info(f"   ✅ Agendamento concluído! {scheduled_count} partidas configuradas")
                else:
                    embed.add_field(
                        name="📬 Nenhuma partida no cache",
                        value="Lembretes serão criados automaticamente quando partidas forem adicionadas",
                        inline=False
                    )
                    logger.warning(f"   ⚠️ Nenhuma partida em cache para agendar")
                
                embed.add_field(
                    name="⚠️ Aviso",
                    value="Configure o canal de notificações com `/canal-notificacoes` antes de ativar!",
                    inline=False
                )
            
            embed.set_footer(text="Bot HLTV - Notificações de Partidas")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            logger.info(f"✓ Notificações {'ativadas' if ativar else 'desativadas'} para guild {guild_id}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar notificações: {e}")
            embed = nextcord.Embed(
                title="❌ Erro",
                description=f"Erro ao configurar notificações: {str(e)}",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @nextcord.slash_command(
        name="canal-notificacoes",
        description="Define o canal onde as notificações serão enviadas"
    )
    async def canal_notificacoes(
        self,
        interaction: nextcord.Interaction,
        canal: nextcord.TextChannel = SlashOption(
            name="canal",
            description="Selecione o canal para notificações",
            required=True
        )
    ):
        """Define o canal para notificações de partidas."""
        
        # Verificar permissões
        if not interaction.user.guild_permissions.administrator:
            embed = nextcord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem configurar canais de notificações.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        channel_id = canal.id
        
        try:
            client = await self.bot.cache_manager.get_client()
            
            # Garantir que existe registro de configuração
            await client.execute(
                """
                INSERT OR IGNORE INTO guild_config (guild_id, notification_channel_id)
                VALUES (?, ?)
                """,
                [guild_id, channel_id]
            )
            
            # Atualizar canal
            await client.execute(
                """
                UPDATE guild_config 
                SET notification_channel_id = ?
                WHERE guild_id = ?
                """,
                [channel_id, guild_id]
            )
            
            embed = nextcord.Embed(
                title="✅ Canal Configurado",
                description=f"As notificações serão enviadas em {canal.mention}",
                color=nextcord.Color.green()
            )
            
            embed.add_field(
                name="📋 Informações",
                value=f"Canal ID: `{channel_id}`\nServidor: `{interaction.guild.name}`",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Próximo Passo",
                value="Use `/notificacoes ativar: verdadeiro` para ativar as notificações",
                inline=False
            )
            
            embed.set_footer(text="Bot HLTV - Notificações de Partidas")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Enviar mensagem no canal
            try:
                embed_test = nextcord.Embed(
                    title="🎮 Notificações Configuradas",
                    description="Este canal foi configurado para receber notificações de partidas de CS2!",
                    color=nextcord.Color.blue()
                )
                embed_test.add_field(
                    name="📬 O que você receberá",
                    value="• Lembretes 1 hora antes da partida\n• Lembretes 30 minutos antes\n• Lembretes 15 minutos antes\n• Lembretes 5 minutos antes\n• Notificação quando a partida inicia",
                    inline=False
                )
                embed_test.set_footer(text="Bot HLTV - Notificações de Partidas")
                
                await canal.send(embed=embed_test)
            except Exception as e:
                logger.warning(f"Não foi possível enviar mensagem de teste no canal: {e}")
            
            logger.info(f"✓ Canal de notificações configurado para guild {guild_id}: {channel_id}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar canal de notificações: {e}")
            embed = nextcord.Embed(
                title="❌ Erro",
                description=f"Erro ao configurar canal: {str(e)}",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @nextcord.slash_command(
        name="notificacoes-resultado",
        description="Ativa/desativa notificações de RESULTADO de partidas"
    )
    async def notificacoes_resultado(
        self,
        interaction: nextcord.Interaction,
        ativar: bool = SlashOption(
            name="ativar",
            description="Ativar ou desativar notificações de resultado",
            required=True
        )
    ):
        """Ativa ou desativa notificações de RESULTADO de partidas finalizadas."""
        
        # Verificar permissões
        if not interaction.user.guild_permissions.administrator:
            embed = nextcord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem configurar notificações.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        
        try:
            client = await self.bot.cache_manager.get_client()
            
            # Garantir que existe registro de configuração
            await client.execute(
                """
                INSERT OR IGNORE INTO guild_config (guild_id, notify_results)
                VALUES (?, ?)
                """,
                [guild_id, 1 if ativar else 0]
            )
            
            # Atualizar configuração
            await client.execute(
                """
                UPDATE guild_config 
                SET notify_results = ?
                WHERE guild_id = ?
                """,
                [1 if ativar else 0, guild_id]
            )
            
            status = "✅ **Ativadas**" if ativar else "❌ **Desativadas**"
            
            embed = nextcord.Embed(
                title="Notificações de Resultado",
                description=f"Notificações de RESULTADO agora estão {status}",
                color=nextcord.Color.green() if ativar else nextcord.Color.red()
            )
            
            if ativar:
                embed.add_field(
                    name="📬 O que você receberá",
                    value="Notificações assim que uma partida termina com o resultado final",
                    inline=False
                )
                embed.add_field(
                    name="⏱️ Tempo de Notificação",
                    value="~1-3 minutos após a partida terminar",
                    inline=False
                )
            
            embed.add_field(
                name="ℹ️ Informação",
                value="Configure o canal com `/canal-notificacoes` para usar esta funcionalidade",
                inline=False
            )
            
            embed.set_footer(text="Bot HLTV - Notificações de Partidas")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            logger.info(f"✓ Notificações de resultado {'ativadas' if ativar else 'desativadas'} para guild {guild_id}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar notificações de resultado: {e}")
            embed = nextcord.Embed(
                title="❌ Erro",
                description=f"Erro ao configurar: {str(e)}",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    """Setup do cog."""
    bot.add_cog(NotificationsCog(bot))
    logger.info("✓ NotificationsCog carregado")
