#!/usr/bin/env python3
"""
Script para testar o algoritmo de scoring com o título real que o usuário encontrou.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.twitch_search_service import TwitchSearchService

# Criar instância do serviço
service = TwitchSearchService()

# Simular o título encontrado: "(ENG) Preasy Mix vs Prestige | POWER Ligaen Season 30"
test_streams = [
    {
        "user_login": "powerligaen",
        "title": "(ENG) Preasy Mix vs Prestige | POWER Ligaen Season 30",
        "viewer_count": 2500,
        "language": "en"
    },
    {
        "user_login": "tck10",
        "title": "C9 TCK RADIANTE MAIOR BÍCEPS VALORANT 🏆!GROWTH🏆",
        "viewer_count": 3789,
        "language": "pt"
    }
]

print("=" * 80)
print("TESTE: Algoritmo de Scoring com Título Real")
print("=" * 80)

print("\n🔍 Testando com:")
print(f'  Championship: "Dust2.dk Ligaen"')
print(f'  Team 1: "Prestige"')
print(f'  Team 2: "Preasy Mix"')

print("\n📊 Streams de entrada:")
for i, stream in enumerate(test_streams, 1):
    print(f"\n  {i}. {stream['user_login']}")
    print(f"     Título: {stream['title']}")
    print(f"     Viewers: {stream['viewer_count']}")

print("\n" + "=" * 80)
print("EXECUTANDO MATCHING")
print("=" * 80)

# Testar o _find_best_match
result = service._find_best_match(
    streams=test_streams,
    query="test",
    language="en",
    championship="Dust2.dk Ligaen",
    team1="Prestige",
    team2="Preasy Mix"
)

print("\n" + "=" * 80)
print("RESULTADO")
print("=" * 80)

if result:
    print(f"\n✅ Stream encontrada!")
    print(f"  Canal: {result['channel_name']}")
    print(f"  URL: {result['url']}")
    print(f"  Viewers: {result['viewer_count']}")
    print(f"  Título: {result['title']}")
else:
    print(f"\n❌ Nenhuma stream válida encontrada")
    print(f"\nA query procurava por:")
    print(f"  - Palavras de 'Dust2.dk Ligaen'")
    print(f"  - Palavras de 'Prestige'")
    print(f"  - Palavras de 'Preasy Mix'")
    print(f"\nMas a stream com título POWER Ligaen não tinha as palavras necessárias.")
