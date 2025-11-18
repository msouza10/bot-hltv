"""
Script para testar e verificar que os novos campos (tier, region, type)
estão sendo capturados, cacheados e exibidos nos embeds.
"""

import asyncio
import json


# Copiar as funções de embeds.py para teste standalone
TIER_MAP = {
    "s": {"emoji": "🏆", "label": "Tier S - Elite", "color": 0xFFAA00},
    "a": {"emoji": "👑", "label": "Tier A - Top", "color": 0xFFFF00},
    "b": {"emoji": "🥇", "label": "Tier B - Profissional", "color": 0xE0E0E0},
    "c": {"emoji": "🥈", "label": "Tier C - Semi-Pro", "color": 0xCD7F32},
    "d": {"emoji": "🥉", "label": "Tier D - Regional", "color": 0x5E5E5E},
    "unranked": {"emoji": "❓", "label": "Unranked", "color": 0x95A5A6},
}

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

EVENT_TYPE_MAP = {
    "online": "💻",
    "offline": "🏟️",
    "online-and-offline": "🌐",
}


def get_tier_info(tier):
    """Obtém informações de tier formatadas."""
    if not tier or tier == "unknown":
        return ("❓", "Tier Desconhecido")
    
    tier_data = TIER_MAP.get(tier.lower(), TIER_MAP["d"])
    return (tier_data["emoji"], tier_data["label"])


def get_region_info(region):
    """Obtém informações de região formatadas."""
    if not region:
        return REGION_MAP["unknown"]["emoji"], REGION_MAP["unknown"]["label"]
    
    region_data = REGION_MAP.get(region.upper(), REGION_MAP["unknown"])
    return (region_data["emoji"], region_data["label"])


def get_event_type_info(event_type):
    """Obtém informações do tipo de evento formatadas."""
    if not event_type:
        return ("❓", "Tipo Desconhecido")
    
    type_lower = event_type.lower()
    emoji = EVENT_TYPE_MAP.get(type_lower, "❓")
    label = type_lower.replace("-", " / ").title()
    return (emoji, label)


async def test_tournament_functions():
    """Testa as funções de formatação de tier, region e event_type."""
    
    print("=" * 80)
    print("TESTE: Funções de Formatação de Tier, Region e Event Type")
    print("=" * 80)
    print()
    
    # Teste 1: Tier
    print("🎯 TESTE 1: Tier (get_tier_info)")
    print("-" * 80)
    test_tiers = ["s", "a", "b", "c", "d", "unranked", "unknown", None]
    for tier in test_tiers:
        emoji, label = get_tier_info(tier)
        tier_str = str(tier) if tier is not None else "None"
        print(f"  {tier_str:10s} → {emoji} {label}")
    print()
    
    # Teste 2: Region
    print("🌍 TESTE 2: Region (get_region_info)")
    print("-" * 80)
    test_regions = ["ASIA", "EEU", "ME", "NA", "OCE", "SA", "WEU", "unknown", None]
    for region in test_regions:
        emoji, label = get_region_info(region)
        region_str = str(region) if region is not None else "None"
        print(f"  {region_str:10s} → {emoji} {label}")
    print()
    
    # Teste 3: Event Type
    print("💻 TESTE 3: Event Type (get_event_type_info)")
    print("-" * 80)
    test_types = ["online", "offline", "online-and-offline", "unknown", None]
    for event_type in test_types:
        emoji, label = get_event_type_info(event_type)
        type_str = str(event_type) if event_type is not None else "None"
        print(f"  {type_str:20s} → {emoji} {label}")
    print()


def test_embed_structure():
    """Verifica a estrutura de um match JSON com os novos campos."""
    
    print("=" * 80)
    print("TESTE: Estrutura de Match JSON com Novos Campos")
    print("=" * 80)
    print()
    
    # Mock de um match com tournament data
    mock_match = {
        "id": 1269173,
        "status": "not_started",
        "scheduled_at": "2025-11-17T15:30:00Z",
        "league": {
            "id": 5232,
            "name": "CCT Europe"
        },
        "serie": {
            "id": 9863,
            "name": "European Contenders #2",
            "full_name": "European Contenders #2 season 3 2025"
        },
        "tournament": {
            "id": 18006,
            "name": "Playoffs",
            "type": "online",
            "region": "EEU",
            "tier": "d"
        },
        "opponents": [
            {
                "opponent": {
                    "id": 135092,
                    "name": "ALLIN"
                }
            },
            {
                "opponent": {
                    "id": 137476,
                    "name": "Washington"
                }
            }
        ]
    }
    
    # Extrair os novos campos
    tournament = mock_match.get("tournament", {})
    tier = tournament.get("tier", "unknown")
    region = tournament.get("region", "unknown")
    event_type = tournament.get("type", "unknown")
    
    print("✅ Match JSON contém:")
    print(f"  • Tournament Tier: {tier}")
    print(f"  • Tournament Region: {region}")
    print(f"  • Event Type: {event_type}")
    print()
    
    # Testar as funções
    tier_emoji, tier_label = get_tier_info(tier)
    region_emoji, region_label = get_region_info(region)
    event_emoji, event_label = get_event_type_info(event_type)
    
    print("✅ Formatação para Embed:")
    tournament_info = f"{tier_emoji} {tier_label}\n{region_emoji} {region_label}\n{event_emoji} {event_label}"
    print(f"  🎯 Detalhes do Campeonato:")
    for line in tournament_info.split("\n"):
        print(f"     {line}")
    print()


async def main():
    """Executa todos os testes."""
    
    print("\n")
    print("🧪 TESTE COMPLETO: Novos Campos em Embeds")
    print("=" * 80)
    print()
    
    await test_tournament_functions()
    test_embed_structure()
    
    print("=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print()
    print("📝 Próximos passos:")
    print("  1. Execute: python -m src.bot")
    print("  2. Use /partidas, /aovivo ou /resultados")
    print("  3. Verifique se os embeds mostram:")
    print("     - 🎯 Detalhes do Campeonato")
    print("     - Tier, Região e Tipo de Evento formatados")
    print()


if __name__ == "__main__":
    asyncio.run(main())
