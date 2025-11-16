#!/usr/bin/env python3
"""
Script de validacao: verifica se mapas, liga, serie, playoff, forfeit estao sendo salvos no cache
"""
import sqlite3
import json

conn = sqlite3.connect('data/bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("\n" + "="*90)
print("VALIDACAO COMPLETA DO CACHE")
print("="*90)

# Buscar uma partida de cada tipo
c.execute('SELECT match_data FROM matches_cache WHERE status = "finished" LIMIT 1')
finished = c.fetchone()

c.execute('SELECT match_data FROM matches_cache WHERE status = "canceled" LIMIT 1')
canceled = c.fetchone()

c.execute('SELECT match_data FROM matches_cache WHERE status = "not_started" LIMIT 1')
future = c.fetchone()

print("\n1. PARTIDA FINALIZADA")
print("-" * 90)
if finished:
    match = json.loads(finished['match_data'])
    
    print(f"ID: {match.get('id')}")
    print(f"Status: {match.get('status')}")
    print(f"League: {match.get('league', {}).get('name')} | Image: {bool(match.get('league', {}).get('image_url'))}")
    
    serie = match.get('serie', {})
    print(f"Serie: {serie.get('full_name', serie.get('name', 'N/A'))}")
    
    tournament = match.get('tournament', {})
    print(f"Tournament: {tournament.get('name', 'N/A')}")
    
    print(f"Match Type: {match.get('match_type')} (playoff? {('playoff' in str(match.get('match_type', '')).lower())})")
    
    print(f"\nDADOS IMPORTANTES:")
    print(f"  [OK] Forfeit: {match.get('forfeit')}")
    print(f"  [OK] Draw: {match.get('draw')}")
    print(f"  [OK] Rescheduled: {match.get('rescheduled')}")
    print(f"  [OK] Version: {match.get('videogame_version')}")
    print(f"  [OK] Results: {match.get('results')}")
    print(f"  [OK] Number of Games: {match.get('number_of_games')}")
    print(f"  [OK] Games count: {len(match.get('games', []))}")
    
    # Verificar games
    games = match.get('games', [])
    if games:
        print(f"\nPRIMEIRO JOGO:")
        game = games[0]
        print(f"  ID: {game.get('id')}")
        print(f"  Status: {game.get('status')}")
        print(f"  Winner: {game.get('winner')}")
        print(f"  Forfeit: {game.get('forfeit')}")
        print(f"  Map: {game.get('map')}")
        print(f"  Teams: {game.get('teams')}")
        print(f"  Results: {game.get('results')}")

print("\n2. PARTIDA CANCELADA")
print("-" * 90)
if canceled:
    match = json.loads(canceled['match_data'])
    
    print(f"ID: {match.get('id')}")
    print(f"Status: {match.get('status')}")
    print(f"League: {match.get('league', {}).get('name')}")
    print(f"Cancellation Reason: {match.get('cancellation_reason', 'N/A')}")

print("\n3. PARTIDA FUTURA")
print("-" * 90)
if future:
    match = json.loads(future['match_data'])
    
    print(f"ID: {match.get('id')}")
    print(f"Status: {match.get('status')}")
    print(f"League: {match.get('league', {}).get('name')}")
    print(f"Serie: {match.get('serie', {}).get('full_name', 'N/A')}")

# Resumo geral
print("\n4. RESUMO DO CACHE")
print("-" * 90)

c.execute('SELECT COUNT(*) as count, status FROM matches_cache GROUP BY status')
rows = c.fetchall()

total = 0
for row in rows:
    print(f"  - {row['status']}: {row['count']}")
    total += row['count']

print(f"  TOTAL: {total}")

# Validacoes
print("\n5. VALIDACOES")
print("-" * 90)

checks = [
    ("Liga/League presente", finished and match.get('league', {}).get('name')),
    ("Imagem da Liga", finished and match.get('league', {}).get('image_url')),
    ("Serie info", finished and match.get('serie', {}).get('full_name')),
    ("Tournament info", finished and match.get('tournament')),
    ("Match Type", finished and match.get('match_type')),
    ("Forfeit flag", finished and 'forfeit' in match),
    ("Draw flag", finished and 'draw' in match),
    ("Videogame Version", finished and match.get('videogame_version')),
    ("Results", finished and match.get('results')),
    ("Games array", finished and match.get('games')),
    ("Number of Games", finished and match.get('number_of_games')),
]

for check_name, result in checks:
    status = "[OK]" if result else "[MISSING]"
    print(f"  {status} {check_name}")

print("\n" + "="*90 + "\n")

conn.close()
