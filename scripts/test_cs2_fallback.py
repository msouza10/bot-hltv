#!/usr/bin/env python3
"""
Script para testar o fallback de busca por CS2 quando o campeonato específico não retorna resultados.

Essa é uma estratégia inteligente: se não achar "CCT Europe",
tenta procurar por "Counter-Strike 2" genérico e depois filtra por times.
"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.twitch_search_service import TwitchSearchService

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Função principal"""
    service = TwitchSearchService()
    
    print("=" * 80)
    print("TESTE: Fallback de Busca por CS2")
    print("=" * 80)
    print("\nCenário: CCT Europe (Betera Esports vs Leo Team)")
    print("Estratégia:")
    print("1. Procurar por 'CCT Europe Betera Esports Leo Team'")
    print("2. Procurar por 'Betera Esports vs Leo Team'")
    print("3. Procurar por 'CCT Europe live'")
    print("4. Procurar por 'CCT Europe'")
    print("5. FALLBACK: Procurar por 'Counter-Strike 2' (genérico)")
    print("6. FALLBACK: Procurar por 'CS2'")
    print()
    
    result = await service.search_streams(
        championship="CCT Europe",
        team1_name="Betera Esports",
        team2_name="Leo Team",
        language="pt"
    )
    
    if result:
        print("\n" + "=" * 80)
        print("✅ STREAM ENCONTRADA!")
        print("=" * 80)
        print(f"Canal: {result['channel_name']}")
        print(f"URL: {result['url']}")
        print(f"Título: {result['title']}")
        print(f"Viewers: {result['viewer_count']:,}")
        print(f"Idioma: {result['language']}")
        print(f"Automatizada: {result['is_automated']}")
    else:
        print("\n" + "=" * 80)
        print("❌ Nenhuma stream encontrada com esse critério")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
