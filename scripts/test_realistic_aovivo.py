#!/usr/bin/env python3
"""
Teste realista: Simula /aovivo com 10 matches como na vida real
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed


def create_mock_match(match_id):
    """Cria mock de um match com streams_list"""
    return {
        "id": match_id,
        "name": f"Team{match_id}A vs Team{match_id}B",
        "status": "running",
        "begin_at": "2025-11-17T18:00:00Z",
        "scheduled_at": "2025-11-17T18:00:00Z",
        "opponents": [
            {"opponent": {"id": 1, "name": f"Team{match_id}A"}},
            {"opponent": {"id": 2, "name": f"Team{match_id}B"}}
        ],
        "league": {"name": "CS2 League"},
        "serie": {"name": "Pro Series"},
        "tournament": {"name": "LAN 2025"},
        "number_of_games": 3,
        "results": [],
        "games": [],
        # IMPORTANTE: Simula dados da API
        "streams_list": [
            {"language": "pt", "raw_url": f"https://twitch.tv/stream{match_id}a", "official": True},
            {"language": "en", "raw_url": f"https://youtube.com/watch?v={match_id}", "official": False}
        ]
    }


async def test_realistic():
    """Testa /aovivo com múltiplos matches (como seria real)"""
    
    print("\n" + "="*80)
    print("🧪 TEST: /aovivo com 10 matches (simulado)")
    print("="*80 + "\n")
    
    # Criar 10 mock matches com streams
    print("1️⃣  Criando 10 mock matches com streams_list...")
    mock_matches = [create_mock_match(i) for i in range(1, 11)]
    print(f"   ✅ {len(mock_matches)} matches criados\n")
    
    # Step 2: Augmentar com paralelo (como faz o código)
    print(f"2️⃣  Augmentando com asyncio.gather()...")
    start = datetime.now()
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    
    augmented = await asyncio.gather(
        *[augment_match_with_streams(m, cache_mgr) for m in mock_matches[:10]],
        return_exceptions=True
    )
    
    augment_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {augment_time:.1f}ms\n")
    
    # Step 3: Criar embeds
    print(f"3️⃣  Criando embeds...")
    start = datetime.now()
    
    embeds = []
    for match in augmented:
        if isinstance(match, Exception):
            continue
        try:
            embed = create_match_embed(match)
            embeds.append(embed)
        except Exception as e:
            print(f"   Error: {e}")
    
    embed_time = (datetime.now() - start).total_seconds() * 1000
    print(f"   ⏱️  {embed_time:.1f}ms | {len(embeds)} embeds\n")
    
    # Step 4: Verificar streams
    print(f"4️⃣  Verificando streams nos embeds...")
    embeds_with_streams = sum(1 for e in embeds if any(f.name == "📡 Streams" for f in e.fields))
    print(f"   ✅ {embeds_with_streams}/{len(embeds)} com streams\n")
    
    total_time = augment_time + embed_time
    
    print("="*80)
    print(f"📊 TOTAL: {total_time:.1f}ms para {len(embeds)} embeds")
    if total_time < 3000:
        print(f"✅ RESULTADO: RÁPIDO! (<3s)")
    else:
        print(f"⚠️  RESULTADO: LENTO! (>{total_time:.0f}ms)")
    print("="*80 + "\n")
    
    return total_time < 3000


async def main():
    result = await test_realistic()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    asyncio.run(main())
