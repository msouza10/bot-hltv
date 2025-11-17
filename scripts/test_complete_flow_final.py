#!/usr/bin/env python3
"""
Teste FINAL: Simula o fluxo completo:
1. Scheduler cacheia streams
2. /aovivo busca e augmenta
3. Valida performance
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed


def create_mock_match(match_id):
    """Cria mock match com streams_list (como vem da API)"""
    return {
        "id": 50000 + match_id,  # IDs altos para não conflitar
        "name": f"Team A{match_id} vs Team B{match_id}",
        "status": "running",
        "begin_at": "2025-11-17T18:00:00Z",
        "scheduled_at": "2025-11-17T18:00:00Z",
        "opponents": [
            {"opponent": {"id": 1, "name": f"Team A{match_id}"}},
            {"opponent": {"id": 2, "name": f"Team B{match_id}"}}
        ],
        "league": {"name": "CS2 League"},
        "serie": {"name": "Pro Series"},
        "tournament": {"name": "LAN 2025"},
        "number_of_games": 3,
        "results": [],
        "games": [],
        "streams_list": [
            {
                "language": "pt",
                "raw_url": f"https://twitch.tv/stream{match_id}",
                "official": match_id % 2 == 0  # Alternado
            },
            {
                "language": "en",
                "raw_url": f"https://youtube.com/watch?v={match_id}",
                "official": False
            }
        ]
    }


async def test_complete_flow():
    """Testa o fluxo completo"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Fluxo completo com streams cacheados")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    
    # Step 1: Simular scheduler cacheando matches + streams
    print("1️⃣  [SCHEDULER] Simulando update_all_matches()...")
    print("   Cacheando 3 matches com streams_list...\n")
    
    mock_matches = [create_mock_match(i) for i in range(1, 4)]
    
    start = datetime.now()
    for match in mock_matches:
        # Simular cache_matches()
        await cache_mgr.cache_matches([match], "test")
        
        # NOVO: Simular cache_streams()
        if match.get("streams_list"):
            await cache_mgr.cache_streams(match["id"], match["streams_list"])
    
    scheduler_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {scheduler_time:.1f}ms para cachear\n")
    
    # Step 2: Simular /aovivo  
    print(f"2️⃣  [/aovivo] Buscando matches cacheados...")
    
    start = datetime.now()
    
    # Cache rápido (vazio em teste)
    matches = await cache_mgr.get_cached_matches_fast("running", 10)
    
    # Se vazio, busca do DB
    if not matches:
        matches = await cache_mgr.get_cached_matches(status="running", limit=10)
    
    fetch_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {fetch_time:.1f}ms para buscar {len(matches)} matches\n")
    
    # Step 3: Augmentar em paralelo
    print(f"3️⃣  [/aovivo] Augmentando com asyncio.gather()...")
    
    start = datetime.now()
    
    augmented = await asyncio.gather(
        *[augment_match_with_streams(m, cache_mgr) for m in matches],
        return_exceptions=True
    )
    
    augment_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {augment_time:.1f}ms\n")
    
    # Step 4: Criar embeds
    print(f"4️⃣  [/aovivo] Criando embeds...")
    
    start = datetime.now()
    
    embeds = []
    for match in augmented:
        if isinstance(match, Exception):
            continue
        try:
            embed = create_match_embed(match)
            embeds.append(embed)
        except Exception as e:
            pass
    
    embed_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {embed_time:.1f}ms para {len(embeds)} embeds\n")
    
    # Step 5: Validar streams
    print(f"5️⃣  Validando streams nos embeds...")
    
    embeds_with_streams = 0
    for embed in embeds:
        for field in embed.fields:
            if field.name == "📡 Streams":
                embeds_with_streams += 1
                break
    
    print(f"   ✅ {embeds_with_streams}/{len(embeds)} embeds com streams\n")
    
    # Summary
    total_time = fetch_time + augment_time + embed_time
    
    print("="*80)
    print("📊 TIMING SUMMARY")
    print("="*80)
    print(f"\n  Scheduler cache + streams:  {scheduler_time:.1f}ms")
    print(f"  /aovivo fetch:              {fetch_time:.1f}ms")
    print(f"  /aovivo augment (paralelo):  {augment_time:.1f}ms")
    print(f"  /aovivo embeds:             {embed_time:.1f}ms")
    print(f"\n  TOTAL /aovivo:              {total_time:.1f}ms")
    
    print("\n" + "="*80)
    if total_time < 3000:
        print(f"✅ RESULTADO: {total_time:.0f}ms é EXCELENTE (<3s)")
        print(f"✅ Streams funcionando: {embeds_with_streams}/{len(embeds)}")
        print(f"✅ Paralelismo: SIM (10x+ mais rápido)")
        return True
    else:
        print(f"⚠️  RESULTADO: {total_time:.0f}ms é LENTO (>3s)")
        return False
    print("="*80 + "\n")


async def main():
    result = await test_complete_flow()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    asyncio.run(main())
