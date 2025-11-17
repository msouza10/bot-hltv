#!/usr/bin/env python3
"""
Teste simples: Just augment + embed creation com mocks
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


async def test_mock_aovivo():
    """Testa /aovivo workflow com mock matches (streams_list)"""
    
    print("\n" + "="*80)
    print("🧪 TEST: /aovivo com mock matches (streams_list da API)")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    
    # Create mock matches COM streams_list (como vem da API)
    mock_matches = [
        {
            "id": 99990 + i,
            "name": f"Team A vs Team B{i}",
            "status": "running",
            "begin_at": "2025-11-17T18:00:00Z",
            "scheduled_at": "2025-11-17T18:00:00Z",
            "opponents": [
                {"opponent": {"id": 1, "name": f"Team A"}},
                {"opponent": {"id": 2, "name": f"Team B{i}"}}
            ],
            "league": {"name": "CS2 League"},
            "serie": {"name": "Pro Series"},
            "tournament": {"name": "LAN 2025"},
            "number_of_games": 3,
            "results": [],
            "games": [],
            "streams_list": [  # IMPORTANTE!
                {"language": "pt", "raw_url": f"https://twitch.tv/s{i}", "official": i % 2 == 0},
                {"language": "en", "raw_url": f"https://youtube.com/watch?v={i}", "official": False}
            ]
        }
        for i in range(1, 6)  # 5 matches
    ]
    
    print(f"1️⃣  {len(mock_matches)} mock matches criados\n")
    
    # Augment em paralelo
    print(f"2️⃣  Augmentando com asyncio.gather()...")
    start = datetime.now()
    
    augmented = await asyncio.gather(
        *[augment_match_with_streams(m, cache_mgr) for m in mock_matches],
        return_exceptions=True
    )
    
    augment_ms = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {augment_ms:.1f}ms\n")
    
    # Create embeds
    print(f"3️⃣  Criando embeds...")
    start = datetime.now()
    
    embeds = []
    for match in augmented:
        if isinstance(match, Exception):
            print(f"   Error: {match}")
            continue
        embed = create_match_embed(match)
        embeds.append(embed)
    
    embed_ms = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {embed_ms:.1f}ms | {len(embeds)} embeds\n")
    
    # Validate streams
    print(f"4️⃣  Verificando streams...")
    with_streams = sum(1 for e in embeds if any(f.name == "📡 Streams" for f in e.fields))
    print(f"   ✅ {with_streams}/{len(embeds)} embeds com streams\n")
    
    total = augment_ms + embed_ms
    
    print("="*80)
    if total < 1000:
        print(f"✅ RÁPIDO! {total:.0f}ms para {len(embeds)} embeds (asyncio.gather + mocks)")
    else:
        print(f"⚠️  Lento: {total:.0f}ms")
    print("="*80 + "\n")
    
    return total < 1000


async def main():
    try:
        result = await test_mock_aovivo()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
