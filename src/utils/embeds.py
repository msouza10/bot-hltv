"""
Utilitários para criar embeds formatados do Discord (usando Nextcord).
"""

import nextcord
from datetime import datetime
from typing import Optional, List, Dict


def create_match_embed(match_data: Dict) -> nextcord.Embed:
    """
    Cria um embed formatado para exibir informações de uma partida.
    
    Args:
        match_data: Dados da partida retornados pela PandaScore API
        
    Returns:
        Embed do Discord formatado
    """
    # Extrair informações básicas
    match_id = match_data.get("id", "N/A")
    status = match_data.get("status", "unknown")
    scheduled_at = match_data.get("scheduled_at")
    begin_at = match_data.get("begin_at")
    
    # Times
    opponents = match_data.get("opponents", [])
    team1 = opponents[0].get("opponent", {}) if len(opponents) > 0 else {}
    team2 = opponents[1].get("opponent", {}) if len(opponents) > 1 else {}
    
    team1_name = team1.get("name", "TBD")
    team2_name = team2.get("name", "TBD")
    
    # Torneio
    league = match_data.get("league", {})
    serie = match_data.get("serie", {})
    tournament = match_data.get("tournament", {})
    
    league_name = league.get("name", "N/A")
    serie_name = serie.get("full_name", serie.get("name", "N/A"))
    tournament_name = tournament.get("name", "N/A")
    
    # Formato
    number_of_games = match_data.get("number_of_games", 1)
    match_type = f"BO{number_of_games}"
    
    # Determinar cor baseada no status
    color_map = {
        "not_started": 0x3498db,  # Azul
        "running": 0xe74c3c,      # Vermelho
        "finished": 0x2ecc71      # Verde
    }
    color = color_map.get(status, 0x95a5a6)  # Cinza padrão
    
    # Emoji de status
    status_emoji = {
        "not_started": "⏰",
        "running": "🔴",
        "finished": "✅"
    }
    emoji = status_emoji.get(status, "📋")
    
    # Criar embed
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=datetime.utcnow()
    )
    
    # Adicionar campos
    embed.add_field(
        name="🏆 Torneio",
        value=f"{league_name}\n{serie_name}",
        inline=False
    )
    
    embed.add_field(
        name="📺 Formato",
        value=match_type,
        inline=True
    )
    
    embed.add_field(
        name="📊 Status",
        value=status.replace("_", " ").title(),
        inline=True
    )
    
    # Horário agendado
    if scheduled_at:
        try:
            dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
            timestamp_discord = f"<t:{int(dt.timestamp())}:F>"
            embed.add_field(
                name="⏰ Horário",
                value=timestamp_discord,
                inline=False
            )
        except:
            embed.add_field(
                name="⏰ Horário",
                value=scheduled_at,
                inline=False
            )
    
    # Resultados (se finalizada)
    if status == "finished":
        results = match_data.get("results", [])
        if results:
            score_text = " - ".join([str(r.get("score", 0)) for r in results])
            embed.add_field(
                name="🎯 Placar",
                value=score_text,
                inline=False
            )
    
    # Links
    links = []
    if match_data.get("official_stream_url"):
        links.append(f"[Stream]({match_data['official_stream_url']})")
    if match_data.get("live_url"):
        links.append(f"[Live]({match_data['live_url']})")
    
    if links:
        embed.add_field(
            name="🔗 Links",
            value=" • ".join(links),
            inline=False
        )
    
    # Thumbnails dos times
    if team1.get("image_url"):
        embed.set_thumbnail(url=team1["image_url"])
    
    embed.set_footer(text=f"Match ID: {match_id} • PandaScore API")
    
    return embed


def create_error_embed(title: str, description: str) -> nextcord.Embed:
    """
    Cria um embed de erro formatado.
    
    Args:
        title: Título do erro
        description: Descrição do erro
        
    Returns:
        Embed de erro
    """
    embed = nextcord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c,  # Vermelho
        timestamp=datetime.utcnow()
    )
    return embed


def create_info_embed(title: str, description: str) -> nextcord.Embed:
    """
    Cria um embed informativo.
    
    Args:
        title: Título
        description: Descrição
        
    Returns:
        Embed informativo
    """
    embed = nextcord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=0x3498db,  # Azul
        timestamp=datetime.utcnow()
    )
    return embed
