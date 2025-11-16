#!/usr/bin/env python3
"""
Verifica se há partidas ao vivo (running) travadas no banco
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("🔍 DEBUG - PARTIDAS AO VIVO (RUNNING) - BANCO DE DADOS")
print("=" * 80)

# Buscar partidas running
cursor.execute('SELECT * FROM matches WHERE status = ? ORDER BY begin_at DESC', ('running',))
running = cursor.fetchall()

print(f'\n📊 Total de partidas ao vivo: {len(running)}\n')

for i, match in enumerate(running, 1):
    print(f'[{i}] {match["name"]}')
    print(f'   ID: {match["id"]}')
    print(f'   Status: {match["status"]}')
    print(f'   Begin_at: {match["begin_at"]}')
    print(f'   Updated_at: {match["updated_at"]}')
    print()

print("=" * 80)
print("⚠️  ANÁLISE DE POSSÍVEIS TRAVAMENTOS:")
print("=" * 80)

# Verificar begin_at NULL
cursor.execute('SELECT COUNT(*) as cnt FROM matches WHERE status = ? AND begin_at IS NULL', ('running',))
null_begin = cursor.fetchone()['cnt']
print(f'❌ Partidas running com begin_at NULL: {null_begin}')

# Verificar updated_at antigo
cursor.execute('''
    SELECT COUNT(*) as cnt FROM matches 
    WHERE status = ? 
    AND datetime(updated_at) < datetime("now", "-5 minutes")
''', ('running',))
old_updates = cursor.fetchone()['cnt']
print(f'⚠️  Partidas running não atualizadas há 5+ min: {old_updates}')

# Mostrar timestamps
print(f'\n⏰ Hora atual: {datetime.now()}')
cursor.execute('SELECT MAX(updated_at) FROM matches')
last_update = cursor.fetchone()[0]
print(f'📅 Última atualização no banco: {last_update}')

# Detalhar quais estão paradas
if old_updates > 0:
    print(f'\n🔴 PARTIDAS PARADAS (não atualizadas há 5+ min):')
    cursor.execute('''
        SELECT id, name, status, updated_at FROM matches 
        WHERE status = ? 
        AND datetime(updated_at) < datetime("now", "-5 minutes")
        ORDER BY updated_at ASC
    ''', ('running',))
    stuck = cursor.fetchall()
    for match in stuck:
        print(f"   • {match['name']} (ID: {match['id']})")
        print(f"     Última atualização: {match['updated_at']}")

conn.close()
