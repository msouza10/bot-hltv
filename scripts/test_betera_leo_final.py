#!/usr/bin/env python3
"""
Teste final: Procurar "Betera vs Leo" usando o novo serviço atualizado.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.twitch_search_service import TwitchSearchService

async def main():
    """Função principal"""
    service = TwitchSearchService()
    
    print("=" * 100)
    print("TESTE FINAL: Procurando 'Betera vs Leo | CCT Europe'")
    print("=" * 100)
    print()
    
    # Simular busca de um match: Betera vs Leo, CCT Europe Season 3
    championship = "CCT Europe"
    team1 = "Betera"
    team2 = "Leo"
    
    print(f"📊 Buscando stream para:")
    print(f"   Campeonato: {championship}")
    print(f"   Time 1: {team1}")
    print(f"   Time 2: {team2}")
    print()
    
    result = await service.search_streams(
        championship=championship,
        team1_name=team1,
        team2_name=team2,
        language="pt"  # Preferência, mas vai aceitar outros idiomas também
    )
    
    if result:
        print("✅ STREAM ENCONTRADA!\n")
        print(f"  Canal: {result['channel_name']}")
        print(f"  URL: {result['url']}")
        print(f"  Título: {result['title']}")
        print(f"  Viewers: {result['viewer_count']:,}")
        print(f"  Idioma: {result.get('language', 'N/A')}")
        print(f"  Automatizada: {'Sim' if result.get('is_automated') else 'Não'}")
    else:
        print("❌ Stream NÃO encontrada")

if __name__ == "__main__":
    asyncio.run(main())
