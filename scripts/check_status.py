#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('data/bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

try:
    print("\n=== DISTRIBUIÇÃO DE STATUS ===")
    c.execute('SELECT status, COUNT(*) as count FROM matches_cache GROUP BY status')
    for row in c.fetchall():
        print(f"{row['status']}: {row['count']}")

    print("\n=== ÚLTIMAS 5 PARTIDAS POR STATUS ===\n")
    
    # Finished
    print("FINISHED:")
    c.execute('''
        SELECT match_id, tournament_name, begin_at, end_at
        FROM matches_cache 
        WHERE status = 'finished'
        ORDER BY end_at DESC 
        LIMIT 3
    ''')
    for row in c.fetchall():
        print(f"  ID: {row['match_id']} | {row['tournament_name']} | End: {row['end_at']}")
    
    # Canceled
    print("\nCANCELED:")
    c.execute('''
        SELECT match_id, tournament_name, begin_at
        FROM matches_cache 
        WHERE status = 'canceled'
        ORDER BY updated_at DESC 
        LIMIT 3
    ''')
    for row in c.fetchall():
        print(f"  ID: {row['match_id']} | {row['tournament_name']} | Begin: {row['begin_at']}")
    
    # Postponed
    print("\nPOSTPONED:")
    c.execute('''
        SELECT match_id, tournament_name, begin_at
        FROM matches_cache 
        WHERE status = 'postponed'
        ORDER BY updated_at DESC 
        LIMIT 3
    ''')
    for row in c.fetchall():
        print(f"  ID: {row['match_id']} | {row['tournament_name']} | Begin: {row['begin_at']}")
        
    print("\n=== CONTAGEM TOTAL ===")
    c.execute('SELECT COUNT(*) as total FROM matches_cache')
    print(f"Total de partidas: {c.fetchone()['total']}")
    
except Exception as e:
    print(f"Erro: {e}")
    
finally:
    conn.close()
