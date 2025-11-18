"""
Utilitários para criar embeds formatados do Discord (usando Nextcord).
"""

import nextcord
from datetime import datetime
from typing import Optional, List, Dict
import pytz
import logging
import re

# Importar TimezoneManager para suporte a timezone
from .timezone_manager import TimezoneManager


# Mapa de bandeiras por idioma (70+ idiomas suportados)
# Cobre 99%+ dos streams reais da API PandaScore
LANGUAGE_FLAGS = {
    # Português
    "pt": "🇵🇹",
    "pt-BR": "🇧🇷",
    "pt-PT": "🇵🇹",
    
    # Inglês
    "en": "🇬🇧",
    "en-US": "🇺🇸",
    "en-GB": "🇬🇧",
    "en-AU": "🇦🇺",
    "en-CA": "🇨🇦",
    "en-NZ": "🇳🇿",
    "en-IN": "��🇳",
    "en-ZA": "🇿🇦",
    
    # Espanhol
    "es": "🇪🇸",
    "es-MX": "🇲🇽",
    "es-AR": "🇦🇷",
    
    # Francês
    "fr": "🇫🇷",
    "fr-CA": "🇨🇦",
    "fr-CH": "🇨🇭",
    "fr-BE": "🇧🇪",
    
    # Alemão
    "de": "🇩🇪",
    "de-AT": "🇦🇹",
    "de-CH": "🇨🇭",
    
    # Russo
    "ru": "🇷🇺",
    
    # Chinês
    "zh": "🇨🇳",
    "zh-Hans": "🇨🇳",
    "zh-Hant": "🇭🇰",
    "zh-TW": "🇹🇼",
    "zh-HK": "🇭🇰",
    
    # Japonês
    "ja": "🇯🇵",
    
    # Coreano
    "ko": "🇰🇷",
    "ko-KR": "🇰🇷",
    
    # Polonês
    "pl": "🇵🇱",
    
    # Turco
    "tr": "🇹🇷",
    
    # Italiano
    "it": "🇮🇹",
    
    # Holandês
    "nl": "🇳🇱",
    "nl-BE": "🇧🇪",
    
    # Sueco
    "sv": "🇸🇪",
    
    # Norueguês
    "no": "🇳🇴",
    "nb": "🇳🇴",
    "nn": "🇳🇴",
    
    # Dinamarquês
    "da": "🇩🇰",
    
    # Finlandês
    "fi": "🇫🇮",
    
    # Grego
    "el": "🇬🇷",
    
    # Húngaro
    "hu": "🇭🇺",
    
    # Tcheco
    "cs": "��🇿",
    
    # Eslovaco
    "sk": "🇸🇰",
    
    # Esloveno
    "sl": "🇸🇮",
    
    # Croata
    "hr": "🇭🇷",
    
    # Sérvio
    "sr": "🇷��",
    
    # Búlgaro
    "bg": "🇧🇬",
    
    # Romeno
    "ro": "🇷🇴",
    
    # Ucraniano
    "uk": "🇺🇦",
    
    # Bielorrusso
    "be": "🇧🇾",
    
    # Hebraico
    "he": "🇮🇱",
    
    # Árabe
    "ar": "🇸🇦",
    
    # Persa
    "fa": "🇮🇷",
    
    # Tailandês
    "th": "🇹��",
    
    # Vietnamita
    "vi": "🇻🇳",
    
    # Indonésio
    "id": "🇮🇩",
    
    # Malaio
    "ms": "🇲🇾",
    
    # Tagalog
    "tl": "��🇭",
    
    # Bengalês
    "bn": "🇧🇩",
    
    # Hindi
    "hi": "🇮🇳",
    
    # Khmer
    "km": "🇰🇭",
    
    # Lao
    "lo": "🇱🇦",
    
    # Birmanês
    "my": "🇲🇲",
    
    # Cingalês
    "si": "🇱🇰",
    
    # Afrikaans
    "af": "🇿🇦",
    
    # Islandês
    "is": "🇮🇸",
    
    # Galego
    "gl": "🇪🇸",
    
    # Basco
    "eu": "🇪🇸",
    
    # Catalão
    "ca": "🇪🇸",
    
    # Maltês
    "mt": "🇲🇹",
    
    # Luxemburguês
    "lb": "🇱🇺",
    
    # Lituano
    "lt": "🇱🇹",
    
    # Letão
    "lv": "🇱🇻",
    
    # Estoniano
    "et": "🇪🇪",
    
    # Georgiano
    "ka": "🇬🇪",
    
    # Armênio
    "hy": "🇦🇲",
    
    # Azerbaijano
    "az": "🇦🇿",
    
    # Cazaque
    "kk": "🇰🇿",
    
    # Uzbeque
    "uz": "🇺🇿",
    
    # Turcomeno
    "tk": "🇹🇲",
    
    # Tadjique
    "tg": "🇹🇯",
    
    # Quirguiz
    "ky": "🇰🇬",
    
    # Suaíli
    "sw": "🇹🇿",
    
    # Igbo
    "ig": "🇳🇬",
    
    # Iorubá
    "yo": "🇳🇬",
    
    # Hauçá
    "ha": "🇳🇬",
    
    # Zulu
    "zu": "🇿🇦",
    
    # Xhosa
    "xh": "🇿🇦",
    
    # Tswana
    "tn": "🇧🇼",
    
    # Quéchua
    "qu": "🇵🇪",
    
    # Aimará
    "ay": "🇧🇴",
    
    # Guarani
    "gn": "🇵🇾",
    
    # Maori
    "mi": "🇳🇿",
    
    # Samoano
    "sm": "🇼🇸",
    
    # Tonganês
    "to": "🇹🇴",
    
    # Fidiano
    "fj": "��🇯",
    
    # Desconhecido
    "unknown": "❓"
}

# Ícones por plataforma
PLATFORM_ICONS = {
    "twitch": "📺",
    "kick": "🎮",
    "youtube": "📹",
    "facebook": "👥",
    "other": "🎥"
}

# Estrela de oficial
OFFICIAL_STAR = "⭐"

# Mapa de tier do campeonato para emoji e cor
# Baseado em: a b c d s unranked (enum da API)
# Ranking: S > A > B > C > D > Unranked
TIER_MAP = {
    "s": {"emoji": "🏆", "label": "Tier S - Elite", "color": 0xFFAA00},
    "a": {"emoji": "👑", "label": "Tier A - Top", "color": 0xFFFF00},
    "b": {"emoji": "🥇", "label": "Tier B - Profissional", "color": 0xE0E0E0},
    "c": {"emoji": "🥈", "label": "Tier C - Semi-Pro", "color": 0xCD7F32},
    "d": {"emoji": "🥉", "label": "Tier D - Regional", "color": 0x5E5E5E},
    "unranked": {"emoji": "❓", "label": "Unranked", "color": 0x95A5A6},
}

# Mapa de regiões para emoji e label
# Baseado em: ASIA EEU ME NA OCE SA WEU (enum da API)
REGION_MAP = {
    "ASIA": {"emoji": "�", "label": "Ásia"},
    "AS": {"emoji": "🌏", "label": "Ásia"},  # Fallback abreviado
    "EEU": {"emoji": "🇪🇺", "label": "Leste Europeu"},
    "ME": {"emoji": "🕌", "label": "Oriente Médio"},
    "NA": {"emoji": "��", "label": "América do Norte"},
    "OCE": {"emoji": "🇦🇺", "label": "Oceania"},
    "SA": {"emoji": "🇧🇷", "label": "América do Sul"},
    "WEU": {"emoji": "🇪�", "label": "Oeste Europeu"},
    "unknown": {"emoji": "🌍", "label": "Regional"},
}

# Mapa de tipo de evento para emoji
EVENT_TYPE_MAP = {
    "online": "💻",
    "offline": "🏟️",
    "online-and-offline": "🌐",
}


def get_tier_info(tier: Optional[str]) -> tuple:
    """
    Obtém informações de tier formatadas.
    
    Args:
        tier: Código do tier (d, c, b, a, s)
        
    Returns:
        Tupla (emoji, label)
    """
    if not tier or tier == "unknown":
        return ("❓", "Tier Desconhecido")
    
    tier_data = TIER_MAP.get(tier.lower(), TIER_MAP["d"])
    return (tier_data["emoji"], tier_data["label"])


def get_region_info(region: Optional[str]) -> tuple:
    """
    Obtém informações de região formatadas.
    
    Args:
        region: Código da região (EEU, WEU, NA, SA, OCE, AS)
        
    Returns:
        Tupla (emoji, label)
    """
    if not region:
        return REGION_MAP["unknown"]["emoji"], REGION_MAP["unknown"]["label"]
    
    region_data = REGION_MAP.get(region.upper(), REGION_MAP["unknown"])
    return (region_data["emoji"], region_data["label"])


def get_event_type_info(event_type: Optional[str]) -> tuple:
    """
    Obtém informações do tipo de evento formatadas.
    
    Args:
        event_type: Tipo do evento (online, offline, online-and-offline)
        
    Returns:
        Tupla (emoji, label)
    """
    if not event_type:
        return ("❓", "Tipo Desconhecido")
    
    type_lower = event_type.lower()
    emoji = EVENT_TYPE_MAP.get(type_lower, "❓")
    label = type_lower.replace("-", " / ").title()
    return (emoji, label)


async def augment_match_with_streams(match_data: Dict, cache_manager) -> Dict:
    """
    Augmenta os dados de match com informações de streams do cache.
    
    ✨ OTIMIZAÇÃO: Se o match tiver streams_list IN MEMORY, formata direto
    sem fazer operações DB. Só busca do cache se não tiver streams_list.
    
    🤖 NOVO: Se não houver streams, busca automaticamente na Twitch
    e adiciona flag is_automated para avisar ao usuário.
    
    Args:
        match_data: Dados do match original
        cache_manager: MatchCacheManager para buscar/cachear streams
        
    Returns:
        match_data com campo 'formatted_streams' adicionado
    """
    try:
        match_id = match_data.get("id")
        if not match_id:
            return match_data
        
        # OTIMIZAÇÃO: Se vem da API com streams_list, formata direto (sem DB!)
        streams_list = match_data.get("streams_list", [])
        if streams_list:
            # Não faz DB aqui - formato direto da API
            # A API retorna os dados estruturados
            formatted = format_streams_field(streams_list, match_data)
            if formatted:
                match_data["formatted_streams"] = formatted
                # Background: cachear para próximas vezes (não bloqueia resposta)
                # Comentado por enquanto para evitar sobrecarga DB
                # asyncio.create_task(cache_manager.cache_streams(match_id, streams_list))
            return match_data
        
        # Se não tem streams_list, buscar do cache (menos frequente)
        streams = await cache_manager.get_match_streams(match_id)
        
        if streams:
            formatted = format_streams_field(streams, match_data)
            match_data["formatted_streams"] = formatted
        else:
            # Sem streams no cache também, tentar busca automática
            # (isso vai cair no logic dentro de format_streams_field)
            formatted = format_streams_field([], match_data)
            if formatted:
                match_data["formatted_streams"] = formatted
                # Adicionar flag para avisar que é busca automática
                match_data["has_automated_streams"] = True
    except Exception as e:
        # Se houver erro, apenas não adiciona streams (graceful degradation)
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Erro ao augmentar match com streams: {e}")
    
    return match_data


def format_streams_field(
    streams: List[Dict],
    match_data: Optional[Dict] = None
) -> Optional[str]:
    """
    Formata lista de streams para exibição no embed.
    
    Suporta 2 formatos:
    1. Dados da API: {raw_url, language, official, main}
    2. Dados do DB: {platform, channel_name, language, is_official, is_main, url, raw_url}
    
    NOVO: Se não houver streams e match_data for fornecido,
    busca automaticamente na Twitch por streams disponíveis.
    
    Formato output:
    Twitch
    - [Gaules](https://twitch.tv/gaules) 🇧🇷 ⭐
    - [eplcs_ru](https://twitch.tv/eplcs_ru) 🇷🇺 🤖
    
    Kick
    - [cct_cs2](https://kick.com/cct_cs2) 🇬🇧
    
    Args:
        streams: Lista de dicts (API ou DB format)
        match_data: Dados do match (opcional) - usado para busca automática
        
    Returns:
        String formatada ou None se sem streams
    """
    if not streams and match_data:
        # Tentar buscar automaticamente na Twitch
        import asyncio
        try:
            # Executar busca de forma assíncrona
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se estamos dentro de async, criar uma task
                # (mais complexo, deixar para depois)
                logger = __import__("logging").getLogger(__name__)
                logger.debug("Pulando busca automática Twitch (já em contexto async)")
                return None
            else:
                # Se não estamos em async, rodar directly
                from src.services.twitch_search_service import get_twitch_search_service
                
                championship = match_data.get("tournament", {}).get("name", "")
                league = match_data.get("league", {}).get("name", "")
                search_name = championship or league or "Game"
                
                opponents = match_data.get("opponents", [])
                team1 = opponents[0].get("opponent", {}).get("name", "Team1") if len(opponents) > 0 else "Team1"
                team2 = opponents[1].get("opponent", {}).get("name", "Team2") if len(opponents) > 1 else "Team2"
                
                twitch_service = loop.run_until_complete(get_twitch_search_service())
                result = loop.run_until_complete(
                    twitch_service.search_streams(search_name, team1, team2)
                )
                
                if result:
                    streams = [result]
        except Exception as e:
            logger = __import__("logging").getLogger(__name__)
            logger.debug(f"Erro ao buscar streams automaticamente: {e}")
            return None
    
    if not streams:
        return None
    
    # ✨ NORMALIZAR: Converter streams da API para formato DB se necessário
    normalized_streams = []
    for stream in streams:
        # Se não tem platform e channel_name, significa que vem da API
        if "platform" not in stream or stream.get("platform") is None:
            # Extrair platform e channel_name da raw_url (ou usar None se não tiver)
            # IMPORTANTE: Usar APENAS raw_url, NÃO embed_url (embed_url é para embeds, não para cliques)
            raw_url = stream.get("raw_url", "")
            if raw_url:
                from src.database.cache_manager import MatchCacheManager
                platform = MatchCacheManager._extract_platform(raw_url)
                channel_name = MatchCacheManager._extract_channel_name(raw_url)
            else:
                platform = "other"
                channel_name = "Unknown"
                raw_url = ""
            
            # Criar versão normalizada
            normalized = {
                "platform": platform,
                "channel_name": channel_name,
                "language": stream.get("language", "unknown"),
                "is_official": stream.get("official", False),  # API usa "official"
                "is_main": stream.get("main", False),  # API usa "main"
                "is_automated": stream.get("is_automated", False),  # Flag de automatizado
                "raw_url": raw_url,  # Guardar a URL para hyperlink
                "title": stream.get("title", ""),  # Título do stream
            }
        else:
            # Já está no formato DB
            normalized = {
                "platform": stream.get("platform", "other"),
                "channel_name": stream.get("channel_name", "Unknown"),
                "language": stream.get("language", "unknown"),
                "is_official": stream.get("is_official", False),
                "is_main": stream.get("is_main", False),
                "is_automated": stream.get("is_automated", False),  # NOVO: preservar flag
                "raw_url": stream.get("url") or stream.get("raw_url", ""),  # DB pode ter 'url' ou 'raw_url'
                "title": stream.get("title", ""),  # Título do stream
            }
        
        normalized_streams.append(normalized)
    
    # Agrupar streams por plataforma
    streams_by_platform = {}
    for stream in normalized_streams:
        platform = stream.get("platform", "other")
        if platform not in streams_by_platform:
            streams_by_platform[platform] = []
        streams_by_platform[platform].append(stream)
    
    result_lines = []
    
    # Ordenar plataformas (twitch/kick primeiro)
    platform_order = ["twitch", "kick", "youtube", "facebook", "other"]
    
    for platform in platform_order:
        if platform not in streams_by_platform:
            continue
        
        platform_streams = streams_by_platform[platform]
        
        # Adicionar cabeçalho da plataforma (sem emoji)
        result_lines.append(f"**{platform.capitalize()}**")
        
        # Listar canais com flag e estrela (com hyperlink!)
        for stream in platform_streams:
            channel_name = stream.get("channel_name", "Unknown")
            language = stream.get("language", "unknown")
            is_official = stream.get("is_official", False)
            is_automated = stream.get("is_automated", False)  # NOVO: flag de automatizado
            raw_url = stream.get("raw_url", "")
            title = stream.get("title", "").strip()
            
            # Para YouTube, tentar usar o título se disponível
            display_name = channel_name
            if platform == "youtube" and title:
                # Limitar tamanho do título para não ficar muito longo
                display_name = title[:50] + "..." if len(title) > 50 else title
            
            # Flag de idioma
            language_flag = LANGUAGE_FLAGS.get(language, "❓")
            
            # Marker de oficial (estrela)
            official_marker = f" -{OFFICIAL_STAR}" if is_official else ""
            
            # Marker de automatizado (robo)
            automated_marker = " -🤖" if is_automated else ""
            
            # Criar hyperlink se tiver URL
            if raw_url:
                channel_link = f"[{display_name}]({raw_url})"
            else:
                channel_link = display_name
            
            # Formato: └ [channel_name](url) - 🇧🇷 -⭐ -🤖
            result_lines.append(f"└ {channel_link} - {language_flag}{official_marker}{automated_marker}")
    
    if not result_lines:
        return None
    
    return "\n".join(result_lines)


def _get_display_datetime_for_match(match_data: Dict, timezone: str) -> Optional[datetime]:
    """
    Retorna o datetime local (timezone-aware) a ser exibido para a partida.
    Prioridade: begin_at -> scheduled_at -> modified_at
    """
    logger = logging.getLogger(__name__)
    candidates = [match_data.get("begin_at"), match_data.get("scheduled_at"), match_data.get("modified_at")]
    for raw in candidates:
        if not raw:
            continue
        try:
            dt_utc = TimezoneManager.parse_iso_datetime(raw)
            if not dt_utc:
                continue
            tz = pytz.timezone(timezone)
            return dt_utc.astimezone(tz)
        except Exception as e:
            logger.debug(f"Erro ao analisar campo de data '{raw}': {e}")
            continue
    return None


def _resolve_tz_abbr_and_offset(timezone: str, dt_local: Optional[datetime] = None) -> tuple:
    """
    Retorna (abbr, offset_str) confiáveis para timezone/instante fornecido.
    Abbreviation: preferência por TimezoneManager.get_timezone_abbreviation() e heurísticas.
    Offset: formato 'UTC±N' calculado a partir do datetime local quando disponível.
    """
    logger = logging.getLogger(__name__)
    abbr = None
    offset_str = None

    # Prefer mapping from TimezoneManager (dictionary), avoid using tzname/tzinfo
    try:
        abbr = TimezoneManager.get_timezone_abbreviation(timezone, dt_local)
    except Exception as e:
        logger.debug(f"TimezoneManager.get_timezone_abbreviation erro: {e}")
        abbr = None

    # Normalize if it's an offset like '-03' or '+02'
    if abbr and re.match(r"^[-+]?\d+$", abbr):
        common_map = {
            "America/Sao_Paulo": "BRT",
            "America/New_York": "EST",
            "Europe/London": "GMT",
            "Asia/Tokyo": "JST",
            "Europe/Paris": "CET",
            "UTC": "UTC",
        }
        abbr = common_map.get(timezone, f"UTC{int(abbr):+d}")

    if dt_local:
        try:
            offset = dt_local.utcoffset()
            if offset is not None:
                total_seconds = int(offset.total_seconds())
                hours = total_seconds // 3600
                minutes = (abs(total_seconds) % 3600) // 60
                sign = "+" if hours >= 0 else "-"
                hours_abs = abs(hours)
                if minutes:
                    offset_str = f"UTC{sign}{hours_abs}:{minutes:02d}"
                else:
                    offset_str = f"UTC{sign}{hours_abs}"
        except Exception as e:
            logger.debug(f"Erro ao calcular utcoffset de dt_local: {e}")

    if not offset_str:
        try:
            offset_str = TimezoneManager.get_timezone_offset(timezone)
        except Exception as e:
            logger.debug(f"TimezoneManager.get_timezone_offset erro: {e}")
            offset_str = "UTC+0"

    if not abbr:
        abbr = "UTC"

    return abbr, offset_str



def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria um embed formatado para exibir informações de uma partida.
    
    Args:
        match_data: Dados da partida retornados pela PandaScore API
        timezone: Timezone para exibição de horários (default: America/Sao_Paulo)
        
    Returns:
        Embed do Discord formatado
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"📍 create_match_embed usando timezone: {timezone}")
    
    # Detectar se é partida futura (para avisar sobre streams)
    status = match_data.get("status", "unknown")
    is_upcoming = status == "not_started"
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
    # Pegar match_type da API e combinar: "BO3 - Best Of"
    api_match_type = match_data.get("match_type", "best_of")
    type_display = api_match_type.replace("_", " ").title() if api_match_type else "Best Of"
    match_type = f"BO{number_of_games} - {type_display}"
    
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
    
    # ✨ NOVO: Criar datetime com timezone awareness (versão híbrida)
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    # Criar embed
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=now_local  # ✅ Com timezone info
    )
    
    # Adicionar campos
    embed.add_field(
        name="🏆 Torneio",
        value=league_name,
        inline=False
    )
    
    embed.add_field(
        name="📍 Série",
        value=serie_name,
        inline=False
    )
    
    # ✨ NOVO: Adicionar informações de tier, região e tipo de evento
    tournament_tier = tournament.get("tier", "unknown")
    tournament_region = tournament.get("region", "unknown")
    event_type = tournament.get("type", "unknown")
    
    tier_emoji, tier_label = get_tier_info(tournament_tier)
    region_emoji, region_label = get_region_info(tournament_region)
    event_emoji, event_label = get_event_type_info(event_type)
    
    # Criar linha com tier, região e tipo em um mesmo campo para economizar espaço
    tournament_info = f"{tier_emoji} {tier_label}\n{region_emoji} {region_label}\n{event_emoji} {event_label}"
    
    embed.add_field(
        name="🎯 Detalhes do Campeonato",
        value=tournament_info,
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
    
    # ⏰ Horário agendado da partida (com timezone)
    display_dt_local = _get_display_datetime_for_match(match_data, timezone)
    if display_dt_local:
        try:
            tz_abbr, tz_offset = _resolve_tz_abbr_and_offset(timezone, display_dt_local)
            weekday_names = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
            weekday = weekday_names.get(display_dt_local.weekday(), "??")
            time_str = display_dt_local.strftime("%H:%M")
            date_str = display_dt_local.strftime("%d/%m")

            # Format: "Terça 18/11 às 19:07 BRT (UTC-3)"
            horario_value = f"{weekday} {date_str} às {time_str} {tz_abbr} ({tz_offset})"

            embed.add_field(
                name="⏰ Horário",
                value=horario_value,
                inline=True
            )
        except Exception as e:
            logger.debug(f"Erro ao formatar horário (match embed): {e}")
    
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
                start = TimezoneManager.parse_iso_datetime(scheduled_at)
                end = TimezoneManager.parse_iso_datetime(end_at)
                if start and end:
                    duration_seconds = (end - start).total_seconds()
                    hours = int(duration_seconds // 3600)
                    minutes = int((duration_seconds % 3600) // 60)
                    duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    embed.add_field(
                        name="⏱️ Duração",
                        value=duration_text,
                        inline=True
                    )
            except Exception as e:
                logger.debug(f"Erro ao calcular duração (match embed): {e}")
    
    # NOVO: Streams disponíveis
    # Nota: Isso será preenchido pelo código que chama create_match_embed
    # Se o match_data contiver "formatted_streams", usamos
    formatted_streams = match_data.get("formatted_streams")
    if formatted_streams:
        # Verificar se há streams automatizados
        has_automated = match_data.get("has_automated_streams", False)
        
        # Para partidas futuras, adicionar aviso sobre possíveis streams
        if is_upcoming:
            aviso_streams = f"{formatted_streams}\n\n📌 ***Transmissão oficial = ⭐***"
            
            # Adicionar aviso se for busca automatizada
            if has_automated:
                aviso_streams += "\n🤖 ***Algumas streams foram encontradas automaticamente e podem não ser oficiais***"
            
            aviso_streams += "\n"
            embed.add_field(
                name="📡 Streams Previstas",
                value=aviso_streams,
                inline=False
            )
        else:
            streams_value = formatted_streams
            
            # Adicionar aviso se for busca automatizada
            if has_automated:
                streams_value += "\n\n🤖 ***Algumas streams foram encontradas automaticamente e podem não ser oficiais***"
            
            embed.add_field(
                name="📡 Streams",
                value=streams_value,
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
    
    # Thumbnails - para futuras, priorizar time 1
    # Logo da liga como imagem grande de background
    league = match_data.get("league", {})
    league_image = league.get("image_url")
    
    if team1.get("image_url"):
        embed.set_thumbnail(url=team1["image_url"])
    
    if league_image:
        embed.set_image(url=league_image)
    
    # Footer com informações importantes
    # ✨ NOVO: Mostrar timezone configurado do servidor (versão híbrida)
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone, display_dt_local or now_local)
    tz_offset = TimezoneManager.get_timezone_offset(timezone)
    
    # Footer format: "Match ID: 123 • PandaScore API • BRT (UTC-3)"
    # O timestamp do Discord já mostra "Hoje às HH:MM" automaticamente!
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr} ({tz_offset})"
    
    embed.set_footer(text=footer_text)
    
    return embed


def create_result_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria um embed otimizado para RESULTADOS de partidas finalizadas.
    Mostra o máximo de informações disponíveis da API.
    
    Args:
        match_data: Dados da partida finalizada
        timezone: Timezone para exibição de horários (default: America/Sao_Paulo)
        
    Returns:
        Embed com resultado completo
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"📍 create_result_embed usando timezone: {timezone}")
    
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
    # Pegar match_type da API e combinar: "BO3 - Best Of"
    api_match_type = match_data.get("match_type", "best_of")
    type_display = api_match_type.replace("_", " ").title() if api_match_type else "Best Of"
    match_type = f"BO{number_of_games} - {type_display}"
    
    # Determinar cor e emoji baseado no status
    if status == "canceled":
        color = 0xe74c3c  # Vermelho para cancelado
        emoji = "❌"
    else:
        color = 0x2ecc71  # Verde para finalizado
        emoji = "✅"
    
    # ✨ NOVO: Criar datetime com timezone awareness (versão híbrida)
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    # Embed
    embed = nextcord.Embed(
        color=color,
        timestamp=now_local  # ✅ Com timezone info
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
    
    # ✨ NOVO: Adicionar informações de tier, região e tipo de evento
    tournament_tier = tournament.get("tier", "unknown")
    tournament_region = tournament.get("region", "unknown")
    event_type = tournament.get("type", "unknown")
    
    tier_emoji, tier_label = get_tier_info(tournament_tier)
    region_emoji, region_label = get_region_info(tournament_region)
    event_emoji, event_label = get_event_type_info(event_type)
    
    # Criar linha com tier, região e tipo em um mesmo campo para economizar espaço
    tournament_details = f"{tier_emoji} {tier_label}\n{region_emoji} {region_label}\n{event_emoji} {event_label}"
    
    embed.add_field(
        name="🎯 Detalhes do Campeonato",
        value=tournament_details,
        inline=False
    )
    
    # Formato e Horário em uma linha
    embed.add_field(
        name="📺 Formato",
        value=match_type,
        inline=True
    )
    
    # ⏰ Horário da partida (com timezone)
    display_dt_local = _get_display_datetime_for_match(match_data, timezone)
    if display_dt_local:
        try:
            tz_abbr, tz_offset = _resolve_tz_abbr_and_offset(timezone, display_dt_local)
            weekday_names = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
            weekday = weekday_names.get(display_dt_local.weekday(), "??")
            time_str = display_dt_local.strftime("%H:%M")
            date_str = display_dt_local.strftime("%d/%m")

            # Format: "Terça 18/11 às 19:07 BRT (UTC-3)"
            horario_value = f"{weekday} {date_str} às {time_str} {tz_abbr} ({tz_offset})"

            embed.add_field(
                name="⏰ Horário",
                value=horario_value,
                inline=True
            )
        except Exception as e:
            logger.debug(f"Erro ao formatar horário (result embed): {e}")
    
    # Placar detalhado - usar results do level superior (não maps individuais)
    # PandaScore não retorna map.name nos dados, mas retorna results com placar final
    results = match_data.get("results", [])
    if status != "canceled" and results and len(results) >= 2:
        # Mostrar placar por BO (Best Of)
        maps_detail = []
        number_of_games = match_data.get("number_of_games", 1)
        
        team1_score = results[0].get("score", 0)
        team2_score = results[1].get("score", 0)
        
        # Pegar match_type da API e combinar: "BO3 - Best Of"
        api_match_type = match_data.get("match_type", "best_of")
        type_display = api_match_type.replace("_", " ").title() if api_match_type else "Best Of"
        match_format = f"BO{number_of_games} - {type_display}"
        maps_detail.append(f"**Resultado Final:** {team1_score}-{team2_score} ({match_format})")
        
        # Se temos games, mostrar um resumo por jogo
        games = match_data.get("games", [])
        if games:
            for i, game in enumerate(games, 1):
                winner = game.get("winner", {})
                
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
                        maps_detail.append(f"🎮 Jogo {i}: {team1_name} venceu{score_text}")
                    elif winner_id == team2_id:
                        maps_detail.append(f"🎮 Jogo {i}: {team2_name} venceu{score_text}")
        
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
            start = TimezoneManager.parse_iso_datetime(begin_at)
            end = TimezoneManager.parse_iso_datetime(end_at)
            if start and end:
                duration_seconds = (end - start).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                embed.add_field(
                    name="⏱️ Duração",
                    value=duration_text,
                    inline=True
                )
        except Exception as e:
            logger.debug(f"Erro ao calcular duração (result embed): {e}")
    
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
    
    # NOVO: Streams disponíveis
    formatted_streams = match_data.get("formatted_streams")
    if formatted_streams:
        embed.add_field(
            name="📡 Streams",
            value=formatted_streams,
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
    # ✨ NOVO: Mostrar timezone configurado do servidor (versão híbrida)
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone, display_dt_local or now_local)
    tz_offset = TimezoneManager.get_timezone_offset(timezone)
    
    # Footer format: "Match ID: 123 • PandaScore API • BRT (UTC-3)"
    # O timestamp do Discord já mostra "Hoje às HH:MM" automaticamente!
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr} ({tz_offset})"
    
    embed.set_footer(text=footer_text)
    
    return embed


def create_error_embed(title: str, description: str, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria um embed de erro formatado.
    
    Args:
        title: Título do erro
        description: Descrição do erro
        timezone: Timezone do servidor (default: America/Sao_Paulo)
        
    Returns:
        Embed de erro
    """
    # ✨ NOVO: Criar datetime com timezone awareness (versão híbrida)
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    embed = nextcord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c,  # Vermelho
        timestamp=now_local  # ✅ Com timezone info
    )
    return embed


def create_info_embed(title: str, description: str, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria um embed informativo.
    
    Args:
        title: Título
        description: Descrição
        timezone: Timezone do servidor (default: America/Sao_Paulo)
        
    Returns:
        Embed informativo
    """
    # ✨ NOVO: Criar datetime com timezone awareness (versão híbrida)
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    embed = nextcord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=0x3498db,  # Azul
        timestamp=now_local  # ✅ Com timezone info
    )
    return embed


def add_automated_stream_info(
    embed: nextcord.Embed,
    stream_data: Dict
) -> nextcord.Embed:
    """
    Adiciona informação de stream automatizada ao embed.
    
    Usa um campo separado para não interferir no design existente.
    Mostra: canal, URL, viewers, idioma, aviso de "não oficial".
    
    Args:
        embed: Embed existente do match
        stream_data: Dados do stream {channel_name, url, viewer_count, language, is_automated}
        
    Returns:
        Embed modificado com informação de stream
    """
    if not stream_data or not stream_data.get("url"):
        return embed
    
    channel_name = stream_data.get("channel_name", "Unknown")
    url = stream_data.get("url", "")
    viewers = stream_data.get("viewer_count", 0)
    language = stream_data.get("language", "unknown")
    
    # Flag de idioma
    language_flag = LANGUAGE_FLAGS.get(language, "❓")
    
    # Formatar viewers
    if viewers > 0:
        if viewers >= 1000:
            viewers_text = f"{viewers/1000:.1f}K 👥"
        else:
            viewers_text = f"{viewers} 👥"
    else:
        viewers_text = "offline"
    
    # Criar link clickável
    channel_link = f"[{channel_name}]({url})"
    
    # Aviso: stream não oficial encontrada por robô
    warning = "⚠️ **Stream Não-Oficial**\n🤖 Encontrada automaticamente por ROBOS!!!\n\n"
    
    # Campo com informações
    stream_info = (
        f"{warning}"
        f"**Canal:** {channel_link}\n"
        f"**Idioma:** {language_flag}\n"
        f"**Viewers:** {viewers_text}"
    )
    
    embed.add_field(
        name="📡 Stream (Automatizada)",
        value=stream_info,
        inline=False
    )
    
    return embed

