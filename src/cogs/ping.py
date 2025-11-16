"""
Cog de teste com comando ping simples.
"""

import nextcord
from nextcord.ext import commands
import logging

logger = logging.getLogger(__name__)


class PingCog(commands.Cog):
    """Comandos de teste simples."""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ PingCog carregado")
    
    @nextcord.slash_command(
        name="ping",
        description="Responde com Pong!"
    )
    async def ping(self, interaction: nextcord.Interaction):
        """Comando simples que responde com Pong!"""
        await interaction.response.send_message("🏓 Pong!")
        logger.info(f"Comando /ping usado por {interaction.user}")


def setup(bot):
    """Função para carregar o cog."""
    bot.add_cog(PingCog(bot))
