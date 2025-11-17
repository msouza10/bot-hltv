#!/usr/bin/env python3
"""
Test script simples para verificar o COALESCE fix sem rodar o bot
"""
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup libSQL connection
from src.database.cache_manager import MatchCacheManager


async def test():
    print("\n" + "="*80)
    print("🧪 TEST: Query com COALESCE(begin_at, updated_at) para /resultados")
    print("="*80 + "\n")
    
    try:
        cache_mgr = MatchCacheManager()
        
        print("1️⃣  Tentando executar get_cached_matches(status='results', limit=5)...")
        print("   ⏱️  Iniciando (timeout de 15 segundos)...\n")
        
        start = asyncio.get_event_loop().time()
        
        matches = await asyncio.wait_for(
            cache_mgr.get_cached_matches(status="results", hours=24, limit=5),
            timeout=15.0
        )
        
        elapsed = asyncio.get_event_loop().time() - start
        
        print(f"   ✅ Sucesso! Tempo: {elapsed:.2f}s")
        print(f"   📊 {len(matches)} matches recuperados\n")
        
        if matches:
            m = matches[0]
            print(f"2️⃣  Primeiro match:")
            print(f"   ID: {m.get('id')}")
            print(f"   Status: {m.get('status')}")
            print(f"   Begin_at: {m.get('begin_at')}")
            print(f"   Updated_at: {m.get('updated_at')}")
        
        print("\n" + "="*80)
        print("✅ RESULTADO: Query executada SEM HANG!")
        print("="*80 + "\n")
        return True
        
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT! Query ainda está travando\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
