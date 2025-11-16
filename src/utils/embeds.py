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
        if results and len(results) >= 2:
            # Placar do match (BO format - ex: 2-0, 2-1)
            team1_score = results[0].get("score", 0)
            team2_score = results[1].get("score", 0)
            
            # Determinar vencedor e formatação especial
            if team1_score > team2_score:
                placar_text = f"🏆 **{team1_name} {team1_score}** - {team2_score} {team2_name}"
            else:
                placar_text = f"{team1_name} {team1_score} - **{team2_score} 🏆 {team2_name}**"
            
            embed.add_field(
                name="🎯 Placar Final",
                value=placar_text,
                inline=False
            )
            
            # Detalhes de cada mapa (se disponível)
            games = match_data.get("games", [])
            if games:
                maps_detail = []
                for i, game in enumerate(games, 1):
                    if game.get("state") == "finished":
                        teams = game.get("teams", [])
                        if len(teams) >= 2:
                            # Identificar qual time é qual e seus scores
                            score1 = teams[0].get("score", 0)
                            score2 = teams[1].get("score", 0)
                            
                            # Determinar vencedor do mapa
                            if score1 > score2:
                                map_result = f"🔴 {team1_name} **{score1}** - {score2} {team2_name}"
                            else:
                                map_result = f"{team1_name} {score1} - **{score2}** 🔴 {team2_name}"
                            
                            maps_detail.append(f"**Mapa {i}:** {map_result}")
                
                if maps_detail:
                    embed.add_field(
                        name="📊 Detalhes dos Mapas",
                        value="\n".join(maps_detail),
                        inline=False
                    )
        
        # Mostrar duração se disponível
        end_at = match_data.get("end_at")
        if scheduled_at and end_at:
            try:
                start = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
                duration = end - start
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60
                duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                embed.add_field(
                    name="⏱️ Duração",
                    value=duration_text,
                    inline=True
                )
            except:
                pass
    
    # Links
    links = []
    if match_data.get("official_stream_url"):
        links.append(f"[Stream]({match_data['official_stream_url']})")
    if match_data.get("live_url"):
        links.append(f"[Live]({match_data['live_url']})")
    
    # Game info
    game_info = []
    videogame = match_data.get("videogame", {})
    if videogame.get("name"):
        game_info.append(videogame["name"])
    
    videogame_version = match_data.get("videogame_version", "")
    if videogame_version:
        game_info.append(f"v{videogame_version}")
    
    combined = links + game_info
    
    if combined:
        embed.add_field(
            name="🔗 Links",
            value=" | ".join(combined),
            inline=False
        )
    
    # Informações extras
    extras = []
    
    # Rescheduled?
    if match_data.get("rescheduled"):
        extras.append("🔄 Partida remarcada")
    
    # Match type info
    match_type_str = match_data.get("match_type", "")
    if match_type_str and match_type_str != "regular":
        extras.append(f"📋 {match_type_str.replace('_', ' ').title()}")
    
    if extras:
        embed.add_field(
            name="ℹ️ Info",
            value=" | ".join(extras),
            inline=True
        )
    
    # Thumbnails - para futuras, priorizar time 1
    # Logo da liga como imagem grande de background
    league = match_data.get("league", {})
    league_image = league.get("image_url")
    
    if team1.get("image_url"):
        embed.set_thumbnail(url=team1["image_url"])
    
    if league_image:
        embed.set_image(url=league_image)
    
    embed.set_footer(text=f"Match ID: {match_id} • PandaScore API")
    
    return embed


def create_result_embed(match_data: Dict) -> nextcord.Embed:
    """
    Cria um embed otimizado para RESULTADOS de partidas finalizadas.
    Mostra o máximo de informações disponíveis da API.
    
    Args:
        match_data: Dados da partida finalizada
        
    Returns:
        Embed com resultado completo
    """
    match_id = match_data.get("id", "N/A")
    status = match_data.get("status", "finished")
    scheduled_at = match_data.get("scheduled_at")
    begin_at = match_data.get("begin_at")
    end_at = match_data.get("end_at")
    
    # Times
    opponents = match_data.get("opponents", [])
    team1_data = opponents[0] if len(opponents) > 0 else {}
    team2_data = opponents[1] if len(opponents) > 1 else {}
    
    team1 = team1_data.get("opponent", {})
    team2 = team2_data.get("opponent", {})
    
    team1_name = team1.get("name", "TBD")
    team2_name = team2.get("name", "TBD")
    team1_result = team1_data.get("result", "unknown")
    team2_result = team2_data.get("result", "unknown")
    
    # Torneio
    league = match_data.get("league", {})
    serie = match_data.get("serie", {})
    tournament = match_data.get("tournament", {})
    
    league_name = league.get("name", "N/A")
    serie_name = serie.get("full_name", serie.get("name", ""))
    tournament_name = tournament.get("name", "N/A")
    
    # Formato
    number_of_games = match_data.get("number_of_games", 1)
    match_type = f"BO{number_of_games}"
    
    # Determinar cor e emoji baseado no status
    if status == "canceled":
        color = 0xe74c3c  # Vermelho para cancelado
        emoji = "❌"
    else:
        color = 0x2ecc71  # Verde para finalizado
        emoji = "✅"
    
    # Embed
    embed = nextcord.Embed(
        color=color,
        timestamp=datetime.utcnow()
    )
    
    # IMPORTANTE: Verificar se é cancelado - se sim, não mostrar placar fake (0-0)
    results = match_data.get("results", [])
    games = match_data.get("games", [])
    
    # Se cancelado, show simples sem placar
    if status == "canceled":
        embed.title = f"{emoji} {team1_name} vs {team2_name} - CANCELADO"
        
        # Motivo do cancelamento (se disponível)
        if match_data.get("cancellation_reason"):
            embed.description = f"**Motivo:** {match_data['cancellation_reason']}"
    else:
        # Se finalizado normalmente, mostrar resultado destacado
        if results and len(results) >= 2:
            team1_score = results[0].get("score", 0)
            team2_score = results[1].get("score", 0)
            
            if team1_score > team2_score:
                title = f"🏆 {team1_name} {team1_score} - {team2_score} {team2_name}"
            else:
                title = f"{team1_name} {team1_score} - {team2_score} {team2_name} 🏆"
            
            embed.title = title
        else:
            embed.title = f"{team1_name} vs {team2_name}"
    
    # Torneio - com detalhes de serie/playoff
    torneio_value = league_name
    
    # Melhorar exibição de série e playoffs
    if serie_name:
        # Verifica se é playoff (match_type pode conter "playoff")
        match_type_val = match_data.get("match_type", "")
        if "playoff" in match_type_val.lower():
            torneio_value += f"\n🏆 **Playoffs:** {serie_name}"
        else:
            torneio_value += f"\n📍 **Serie:** {serie_name}"
    
    if tournament_name and tournament_name != "N/A":
        # Tournament geralmente é a fase (Group A, Semi-finals, etc)
        torneio_value += f"\n→ {tournament_name}"
    
    embed.add_field(
        name="🏆 Torneio",
        value=torneio_value,
        inline=False
    )
    
    # Formato e Horário em uma linha
    embed.add_field(
        name="📺 Formato",
        value=match_type,
        inline=True
    )
    
    if scheduled_at:
        try:
            dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
            timestamp_discord = f"<t:{int(dt.timestamp())}:f>"
            embed.add_field(
                name="📅 Data",
                value=timestamp_discord,
                inline=True
            )
        except:
            pass
    
    # Placar detalhado - usar results do level superior (não maps individuais)
    # PandaScore não retorna map.name nos dados, mas retorna results com placar final
    results = match_data.get("results", [])
    if status != "canceled" and results and len(results) >= 2:
        # Mostrar placar por BO (Best Of)
        maps_detail = []
        number_of_games = match_data.get("number_of_games", 1)
        
        team1_score = results[0].get("score", 0)
        team2_score = results[1].get("score", 0)
        
        # Exibir em formato BO3, BO5, etc
        match_format = f"BO{number_of_games}"
        maps_detail.append(f"**Resultado Final:** {team1_score}-{team2_score} ({match_format})")
        
        # Se temos games, mostrar um resumo por jogo
        games = match_data.get("games", [])
        if games:
            for i, game in enumerate(games, 1):
                winner = game.get("winner", {})
                # Tentar extrair o nome do mapa
                map_data = game.get("map", {})
                map_name = map_data.get("name", "???") if isinstance(map_data, dict) else str(map_data)
                
                if winner:
                    winner_id = winner.get("id")
                    team1_id = opponents[0].get("opponent", {}).get("id") if len(opponents) > 0 else None
                    team2_id = opponents[1].get("opponent", {}).get("id") if len(opponents) > 1 else None
                    
                    # Tentar extrair placar do jogo
                    game_results = game.get("results", [])
                    score_text = ""
                    if game_results and len(game_results) >= 2:
                        score_text = f" {game_results[0].get('score', '?')}-{game_results[1].get('score', '?')}"
                    
                    if winner_id == team1_id:
                        maps_detail.append(f"🗺️ Mapa {i} ({map_name}): {team1_name} venceu{score_text}")
                    elif winner_id == team2_id:
                        maps_detail.append(f"🗺️ Mapa {i} ({map_name}): {team2_name} venceu{score_text}")
        
        if maps_detail:
            maps_text = "\n".join(maps_detail[:8])
            embed.add_field(
                name="📊 Resultado dos Mapas",
                value=maps_text,
                inline=False
            )
    
    # Duração da partida (APENAS se não foi cancelado e tem timestamps)
    if status != "canceled" and begin_at and end_at:
        try:
            start = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
            duration = end - start
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            embed.add_field(
                name="⏱️ Duração",
                value=duration_text,
                inline=True
            )
        except:
            pass
    
    # Status especial (cancelado, adiado, etc)
    if status != "finished":
        status_display = status.replace("_", " ").title()
        if status == "canceled":
            status_display = "Cancelado"
        embed.add_field(
            name="⚠️ Status",
            value=status_display,
            inline=True
        )
    
    # Informações extras baseadas em status
    extras = []
    
    # 1. Forfeit - MUITO IMPORTANTE: vitória por abandono do oponente
    if status == "finished" and match_data.get("forfeit"):
        # Identificar qual time venceu por forfeit
        results_data = match_data.get("results", [])
        winner_id = match_data.get("winner_id")
        
        forfeit_text = "⚠️ **Vitória por Forfeit**"
        if winner_id:
            if len(opponents) > 0 and opponents[0].get("opponent", {}).get("id") == winner_id:
                forfeit_text += f"\n{team1_name} venceu por abandono de {team2_name}"
            elif len(opponents) > 1 and opponents[1].get("opponent", {}).get("id") == winner_id:
                forfeit_text += f"\n{team2_name} venceu por abandono de {team1_name}"
        
        extras.append(forfeit_text)
    
    # 2. Empate - série empatada
    if status == "finished" and match_data.get("draw"):
        extras.append("🤝 **Série Empatada**")
    
    # 3. Versão do jogo
    videogame_version = match_data.get("videogame_version", "")
    if videogame_version:
        extras.append(f"🎮 **Versão:** {videogame_version}")
    
    # 4. Rescheduled - partida remarcada
    if match_data.get("rescheduled"):
        extras.append("🔄 **Partida Remarcada**")
    
    # 5. Match type especial (apenas se não for regular/best_of)
    match_type_str = match_data.get("match_type", "")
    if match_type_str and match_type_str not in ["regular", "best_of", "best of"]:
        type_display = match_type_str.replace('_', ' ').title()
        extras.append(f"📋 **Tipo Especial:** {type_display}")
    
    if extras:
        embed.add_field(
            name="ℹ️ Detalhes",
            value="\n".join(extras),
            inline=False
        )
    
    # Links
    links = []
    if match_data.get("official_stream_url"):
        links.append(f"[Stream]({match_data['official_stream_url']})")
    if match_data.get("live_url"):
        links.append(f"[Detalhes]({match_data['live_url']})")
    
    # Game info
    game_info = []
    videogame = match_data.get("videogame", {})
    if videogame.get("name"):
        game_info.append(videogame["name"])
    
    # Remover IDs - não são necessários na exibição pública
    # (Manter comentário para referência interna se precisar análises)
    
    combined_info = links + game_info
    
    if combined_info:
        embed.add_field(
            name="🔗 Informações",
            value=" | ".join(combined_info),
            inline=False
        )
    
    # Thumbnails - preferência: time vencedor > liga > time 1
    # Para partidas finalizadas, prioritizar time vencedor
    winner_image = None
    if status == "finished":
        winner_id = match_data.get("winner_id")
        if winner_id:
            # Encontrar qual time venceu
            for opponent in opponents:
                if opponent.get("opponent", {}).get("id") == winner_id:
                    winner_image = opponent.get("opponent", {}).get("image_url")
                    break
    
    # Prioridade de thumbnail: vencedor > liga > time 1
    if winner_image:
        embed.set_thumbnail(url=winner_image)
    elif league.get("image_url"):
        embed.set_thumbnail(url=league.get("image_url"))
    elif team1.get("image_url"):
        embed.set_thumbnail(url=team1["image_url"])
    
    # Usar logo da liga como imagem grande de background visual
    league_image = league.get("image_url")
    if league_image:
        embed.set_image(url=league_image)
    
    # Footer com informações importantes
    footer_text = f"ID: {match_id}"
    
    # Adicionar timestamp no footer se disponível
    if status == "finished" and begin_at:
        try:
            start = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
            footer_text += f" • {start.strftime('%d/%m %H:%M')} UTC"
        except:
            pass
    
    embed.set_footer(text=footer_text)
    
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
