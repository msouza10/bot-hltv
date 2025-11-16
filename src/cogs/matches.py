"""
Cog para comandos relacionados a partidas de CS2 (usando Nextcord).
"""

import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging
from typing import Optional

from src.utils.embeds import create_match_embed, create_error_embed, create_info_embed

logger = logging.getLogger(__name__)


class MatchesCog(commands.Cog):
    """Comandos para consultar partidas de CS2."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(
        name="partidas",
        description="Mostra as próximas partidas de CS2"
    )
    async def partidas(
        self,
        interaction: nextcord.Interaction,
        quantidade: int = SlashOption(
            name="quantidade",
            description="Quantidade de partidas a exibir (máx: 10)",
            min_value=1,
            max_value=10,
            default=5,
            required=False
        )
    ):
        """Lista as próximas partidas de CS2."""
        await interaction.response.defer()
        
        try:
            # Buscar partidas da API
            matches = await self.bot.api_client.get_upcoming_matches(per_page=quantidade)
            
            if not matches:
                embed = create_info_embed(
                    "Nenhuma partida encontrada",
                    "Não há partidas agendadas no momento."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Criar embeds para cada partida
            embeds = []
            for match in matches[:quantidade]:
                try:
                    embed = create_match_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed para partida {match.get('id')}: {e}")
            
            if not embeds:
                embed = create_error_embed(
                    "Erro ao processar partidas",
                    "Não foi possível processar as informações das partidas."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Enviar resposta
            await interaction.followup.send(
                content=f"**📋 Próximas {len(embeds)} partidas de CS2:**",
                embeds=embeds[:10]  # Discord limita a 10 embeds por mensagem
            )
            
            logger.info(f"✓ Comando /partidas executado por {interaction.user} ({quantidade} partidas)")
            
        except Exception as e:
            logger.error(f"✗ Erro no comando /partidas: {e}")
            embed = create_error_embed(
                "Erro ao buscar partidas",
                f"Ocorreu um erro ao consultar a API: {str(e)}"
            )
            await interaction.followup.send(embed=embed)
    
    @nextcord.slash_command(
        name="aovivo",
        description="Mostra partidas de CS2 acontecendo agora"
    )
    async def aovivo(self, interaction: nextcord.Interaction):
        """Lista partidas ao vivo."""
        await interaction.response.defer()
        
        try:
            matches = await self.bot.api_client.get_running_matches()
            
            if not matches:
                embed = create_info_embed(
                    "Nenhuma partida ao vivo",
                    "Não há partidas acontecendo no momento."
                )
                await interaction.followup.send(embed=embed)
                return
            
            embeds = []
            for match in matches[:10]:
                try:
                    embed = create_match_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed: {e}")
            
            if embeds:
                await interaction.followup.send(
                    content=f"**🔴 {len(embeds)} partida(s) ao vivo:**",
                    embeds=embeds
                )
            
            logger.info(f"✓ Comando /aovivo executado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"✗ Erro no comando /aovivo: {e}")
            embed = create_error_embed(
                "Erro ao buscar partidas",
                f"Ocorreu um erro: {str(e)}"
            )
            await interaction.followup.send(embed=embed)
    
    @nextcord.slash_command(
        name="resultados",
        description="Mostra resultados recentes de partidas de CS2"
    )
    async def resultados(
        self,
        interaction: nextcord.Interaction,
        horas: int = SlashOption(
            name="horas",
            description="Buscar resultados das últimas X horas (máx: 72)",
            min_value=1,
            max_value=72,
            default=24,
            required=False
        ),
        quantidade: int = SlashOption(
            name="quantidade",
            description="Quantidade de partidas a exibir (máx: 10)",
            min_value=1,
            max_value=10,
            default=5,
            required=False
        )
    ):
        """Lista resultados recentes."""
        await interaction.response.defer()
        
        try:
            matches = await self.bot.api_client.get_past_matches(
                hours=horas,
                per_page=quantidade
            )
            
            if not matches:
                embed = create_info_embed(
                    "Nenhum resultado encontrado",
                    f"Não há resultados das últimas {horas} horas."
                )
                await interaction.followup.send(embed=embed)
                return
            
            embeds = []
            for match in matches[:quantidade]:
                try:
                    embed = create_match_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed: {e}")
            
            if embeds:
                await interaction.followup.send(
                    content=f"**✅ Últimos {len(embeds)} resultado(s) ({horas}h):**",
                    embeds=embeds
                )
            
            logger.info(f"✓ Comando /resultados executado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"✗ Erro no comando /resultados: {e}")
            embed = create_error_embed(
                "Erro ao buscar resultados",
                f"Ocorreu um erro: {str(e)}"
            )
            await interaction.followup.send(embed=embed)


def setup(bot):
    """Adiciona o cog ao bot."""
    bot.add_cog(MatchesCog(bot))
