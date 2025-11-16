#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('data/bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 100)
print("ANÁLISE: O QUE ESTÁ SENDO ARMAZENADO NO CACHE")
print("=" * 100)

# Buscar uma partida finalizada
c.execute('SELECT match_data FROM matches_cache WHERE status = "finished" LIMIT 1')
row = c.fetchone()

if row:
    match = json.loads(row['match_data'])
    print("\n📊 ESTRUTURA DE UMA PARTIDA FINALIZADA:")
    print(f"\nMatch ID: {match.get('id')}")
    print(f"Status: {match.get('status')}")
    
    print("\n🗺️ MAPAS (games):")
    games = match.get('games', [])
    print(f"Total de mapas: {len(games)}")
    
    if games:
        for i, game in enumerate(games, 1):
            print(f"\n  Mapa {i}:")
            print(f"    - ID: {game.get('id')}")
            print(f"    - State: {game.get('state')}")
            print(f"    - Map: {game.get('map')}")
            print(f"    - Teams: {game.get('teams')}")
            print(f"    - Results: {game.get('results')}")
    
    print("\n🏆 SÉRIE/PLAYOFF INFO:")
    print(f"  - Serie: {match.get('serie')}")
    print(f"  - Serie ID: {match.get('serie_id')}")
    print(f"  - Match Type: {match.get('match_type')}")
    print(f"  - League: {match.get('league')}")
    print(f"  - League ID: {match.get('league_id')}")
    print(f"  - Tournament: {match.get('tournament')}")
    
    print("\n⚠️ FORFEIT E DRAW:")
    print(f"  - Forfeit: {match.get('forfeit')}")
    print(f"  - Draw: {match.get('draw')}")
    
    print("\n🎮 IMAGENS E LOGOS:")
    print(f"  - League Image: {match.get('league', {}).get('image_url')}")
    print(f"  - Team1 Image: {match.get('opponents', [{}])[0].get('opponent', {}).get('image_url') if len(match.get('opponents', [])) > 0 else 'N/A'}")
    print(f"  - Videogame: {match.get('videogame')}")
    
    print("\n📋 TODOS OS CAMPOS DISPONÍVEIS:")
    print(f"  {list(match.keys())}")

else:
    print("❌ Nenhuma partida finalizada encontrada")

conn.close()
print("\n" + "=" * 100)
