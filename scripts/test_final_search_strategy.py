#!/usr/bin/env python3
"""
Teste final: Nova estratégia de busca usando game_id + scoring
Isso deve ser MUITO mais confiável que busca textual.
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
    
    print("=" * 90)
    print("TESTE FINAL: Busca por game_id + Scoring")
    print("=" * 90)
    print("\nEstratégia MELHORADA:")
    print("1. Usar game_id=32399 (Counter-Strike genérico)")
    print("2. Retorna streams EM TEMPO REAL")
    print("3. Depois aplicar scoring por campeonato/times no código")
    print("\nCenário: CCT Europe (Betera Esports vs Leo Team)\n")
    
    result = await service.search_streams(
        championship="CCT Europe",
        team1_name="Betera Esports",
        team2_name="Leo Team",
        language="pt"
    )
    
    if result:
        print("\n" + "=" * 90)
        print("✅ STREAM ENCONTRADA!")
        print("=" * 90)
        print(f"Canal: {result['channel_name']}")
        print(f"URL: {result['url']}")
        print(f"Título: {result['title']}")
        print(f"Viewers: {result['viewer_count']:,}")
        print(f"Idioma: {result['language']}")
        print(f"Automatizada: {result['is_automated']}")
        print("=" * 90)
    else:
        print("\n" + "=" * 90)
        print("❌ Nenhuma stream encontrada")
        print("=" * 90)
        print("\nIsso é esperado se:")
        print("1. Não há streams ao vivo neste momento")
        print("2. Streams ao vivo não têm 'Betera' ou 'Leo' no título")
        print("3. Scores estão abaixo do mínimo configurado")
        print("\nMas diferente de antes, NÃO é por problema de indexação!")

if __name__ == "__main__":
    asyncio.run(main())
