"""
Cog para comandos relacionados a partidas de CS2 (usando Nextcord).
"""

import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging
from typing import Optional

from src.utils.embeds import create_match_embed, create_result_embed, create_error_embed, create_info_embed, augment_match_with_streams

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
        """Lista as próximas partidas de CS2 (do cache rápido)."""
        await interaction.response.defer()
        
        try:
            # Primeiro: tentar cache em memória (muito rápido!)
            matches = await self.bot.cache_manager.get_cached_matches_fast("upcoming", quantidade)
            
            # Se vazio: buscar do banco (mais lento)
            if not matches:
                logger.info("Cache em memória vazio, buscando do banco...")
                matches = await self.bot.cache_manager.get_cached_matches(
                    status="not_started",
                    limit=quantidade
                )
            
            # Última opção: API (só se tudo vazio)
            if not matches:
                logger.info("Cache vazio, buscando da API...")
                matches = await self.bot.api_client.get_upcoming_matches(per_page=quantidade)
            
            if not matches:
                embed = create_info_embed(
                    "Nenhuma partida encontrada",
                    "Não há partidas agendadas no momento."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Criar embeds para cada partida - augmentar em paralelo
            augmented_matches = await asyncio.gather(
                *[augment_match_with_streams(m, self.bot.cache_manager) for m in matches[:quantidade]],
                return_exceptions=True
            )
            
            embeds = []
            for match in augmented_matches:
                try:
                    if isinstance(match, Exception):
                        logger.error(f"Erro ao augmentar match: {match}")
                        continue
                    embed = create_match_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed: {e}")
            
            if not embeds:
                embed = create_error_embed(
                    "Erro ao processar partidas",
                    "Não foi possível processar as informações das partidas."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Enviar resposta
            await interaction.followup.send(
                content=f"**📋 Próximas {len(embeds)} partidas de CS2:** (cache atualizado)",
                embeds=embeds[:10]  # Discord limita a 10 embeds por mensagem
            )
            
            logger.info(f"✓ Comando /partidas executado por {interaction.user} ({quantidade} partidas do cache)")
            
        except Exception as e:
            logger.error(f"✗ Erro no comando /partidas: {e}")
            embed = create_error_embed(
                "Erro ao buscar partidas",
                f"Ocorreu um erro ao consultar o cache: {str(e)}"
            )
            await interaction.followup.send(embed=embed)
    
    @nextcord.slash_command(
        name="aovivo",
        description="Mostra partidas de CS2 acontecendo agora"
    )
    async def aovivo(self, interaction: nextcord.Interaction):
        """Lista partidas ao vivo (do cache rápido)."""
        await interaction.response.defer()
        
        try:
            # Primeiro: tentar cache em memória (muito rápido!)
            matches = await self.bot.cache_manager.get_cached_matches_fast("running", 10)
            
            # Se vazio: buscar do banco (mais lento)
            if not matches:
                logger.info("Cache em memória vazio, buscando do banco...")
                matches = await self.bot.cache_manager.get_cached_matches(
                    status="running",
                    limit=10
                )
            
            # Última opção: API
            if not matches:
                logger.info("Nenhuma partida ao vivo no cache, buscando da API...")
                matches = await self.bot.api_client.get_running_matches()
            
            if not matches:
                embed = create_info_embed(
                    "Nenhuma partida ao vivo",
                    "Não há partidas acontecendo no momento."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Augmentar todos os matches com streams em paralelo
            augmented_matches = await asyncio.gather(
                *[augment_match_with_streams(m, self.bot.cache_manager) for m in matches[:10]],
                return_exceptions=True
            )
            
            embeds = []
            for match in augmented_matches:
                try:
                    if isinstance(match, Exception):
                        logger.error(f"Erro ao augmentar match: {match}")
                        continue
                    embed = create_match_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed: {e}")
            
            if embeds:
                await interaction.followup.send(
                    content=f"**🔴 {len(embeds)} partida(s) ao vivo:** (cache atualizado)",
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
        """Lista resultados recentes (do cache rápido)."""
        await interaction.response.defer()
        
        try:
            # Primeiro: tentar cache em memória (muito rápido!)
            matches = await self.bot.cache_manager.get_cached_matches_fast("finished", quantidade)
            
            # Se vazio: buscar do banco (mais lento)
            if not matches:
                logger.info("Cache em memória vazio, buscando do banco...")
                matches = await self.bot.cache_manager.get_cached_matches(
                    status="results",  # Inclui finished, canceled, postponed
                    hours=horas,
                    limit=quantidade
                )
            
            # Última opção: API
            if not matches:
                logger.info("Nenhum resultado no cache, buscando da API...")
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
            
            # Augmentar todos os matches com streams em paralelo
            augmented_matches = await asyncio.gather(
                *[augment_match_with_streams(m, self.bot.cache_manager) for m in matches[:quantidade]],
                return_exceptions=True
            )
            
            embeds = []
            for match in augmented_matches:
                try:
                    if isinstance(match, Exception):
                        logger.error(f"Erro ao augmentar match: {match}")
                        continue
                    # Usar função otimizada para resultados
                    embed = create_result_embed(match)
                    embeds.append(embed)
                except Exception as e:
                    logger.error(f"Erro ao criar embed: {e}")
            
            if embeds:
                await interaction.followup.send(
                    content=f"**✅ Últimos {len(embeds)} resultado(s) ({horas}h):** (cache atualizado)",
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
