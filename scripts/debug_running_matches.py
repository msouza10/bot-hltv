#!/usr/bin/env python3
"""
Debug script para verificar partidas ao vivo (running) no cache
"""
import sys
sys.path.insert(0, '/root/workspace')

from datetime import datetime
from src.database.cache_manager import MatchCacheManager

# Inicializar cache
cache = MatchCacheManager()

print("=" * 80)
print("🔍 DEBUG - PARTIDAS AO VIVO (RUNNING)")
print("=" * 80)

# Buscar partidas ao vivo
running = cache.get_cached_matches("running")
print(f"\n📊 Total de partidas ao vivo: {len(running)}\n")

for i, match in enumerate(running, 1):
    print(f"[{i}] {match.get('name', 'N/A')}")
    print(f"   ID: {match['id']}")
    print(f"   Status: {match['status']}")
    print(f"   Begin_at: {match.get('begin_at', 'NULL')}")
    print(f"   Updated_at: {match.get('updated_at', 'NULL')}")
    print(f"   Scheduled_at: {match.get('scheduled_at', 'NULL')}")
    print(f"   Result: {match.get('results', [])}")
    
    # Verificar horário
    begin = match.get('begin_at')
    if begin:
        try:
            from datetime import timezone
            begin_dt = datetime.fromisoformat(begin.replace('Z', '+00:00'))
            begin_local = begin_dt.astimezone().replace(tzinfo=None)
            now = datetime.now()
            diff = begin_local - now
            print(f"   ⏰ Começou em: {begin_local} (diferença: {diff})")
        except:
            print(f"   ⏰ Erro ao parsear horário")
    
    print()

print("=" * 80)
print("⚠️ POSSÍVEIS PROBLEMAS:")
print("=" * 80)
print("1. Partidas com begin_at NULL (podem estar travadas)")
print("2. Partidas com updated_at muito antigo")
print("3. Status 'running' mas já deveriam estar 'finished'")
print("=" * 80)
