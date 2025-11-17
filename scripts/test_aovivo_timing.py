#!/usr/bin/env python3
"""
Teste de performance completo do /aovivo com timing detalhado
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv()
LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed


async def test_aovivo_performance():
    """Testa cada passo do /aovivo e mede timing"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Performance detalhado do /aovivo")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    timings = {}
    
    try:
        # Step 1: get_cached_matches_fast() - deve ser <10ms
        print("1️⃣  get_cached_matches_fast('running', 10)...")
        start = datetime.now()
        matches = await cache_mgr.get_cached_matches_fast("running", 10)
        timings["fast_cache"] = (datetime.now() - start).total_seconds() * 1000
        print(f"   ⏱️  {timings['fast_cache']:.1f}ms | {len(matches)} matches\n")
        
        # Se vazio, fazer slow query
        if not matches:
            print("2️⃣  get_cached_matches('running') [cache vazio]...")
            start = datetime.now()
            matches = await asyncio.wait_for(
                cache_mgr.get_cached_matches(status="running", limit=10),
                timeout=15.0
            )
            timings["slow_cache"] = (datetime.now() - start).total_seconds() * 1000
            print(f"   ⏱️  {timings['slow_cache']:.1f}ms | {len(matches)} matches\n")
        
        if not matches:
            print("   ℹ️  Nenhum match em running - teste incompleto\n")
            return True
        
        # Step 2: asyncio.gather para augment
        print(f"3️⃣  asyncio.gather() para {len(matches)} matches...")
        start = datetime.now()
        
        augmented = await asyncio.gather(
            *[augment_match_with_streams(m, cache_mgr) for m in matches[:10]],
            return_exceptions=True
        )
        
        timings["augment_gather"] = (datetime.now() - start).total_seconds() * 1000
        print(f"   ⏱️  {timings['augment_gather']:.1f}ms\n")
        
        # Step 3: create_match_embed() para cada um
        print(f"4️⃣  create_match_embed() para {len(augmented)} matches...")
        start = datetime.now()
        
        embeds = []
        for match in augmented:
            if isinstance(match, Exception):
                continue
            embed = create_match_embed(match)
            embeds.append(embed)
        
        timings["embed_creation"] = (datetime.now() - start).total_seconds() * 1000
        print(f"   ⏱️  {timings['embed_creation']:.1f}ms | {len(embeds)} embeds\n")
        
        # Step 5: Enviar resposta (simular)
        print(f"5️⃣  Simular envio...")
        print(f"   ✅ Teria enviado {len(embeds)} embeds\n")
        
        # Summary
        print("="*80)
        print("📊 TIMING SUMMARY")
        print("="*80 + "\n")
        
        total_time = sum(timings.values())
        
        for step, ms in timings.items():
            pct = (ms / total_time * 100) if total_time > 0 else 0
            bar_width = int(pct / 5)
            bar = "█" * bar_width
            print(f"  {step:.<30} {ms:>7.1f}ms ({pct:>5.1f}%) {bar}")
        
        print(f"\n  {'TOTAL':.<30} {total_time:>7.1f}ms")
        
        print("\n" + "="*80)
        if total_time < 3000:
            print(f"✅ RESULTADO: {total_time:.0f}ms é ACEITÁVEL (<3s)")
        else:
            print(f"⚠️  RESULTADO: {total_time:.0f}ms é LENTO (>3s)")
        print("="*80 + "\n")
        
        return total_time < 3000
        
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT!\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    result = await test_aovivo_performance()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    asyncio.run(main())
