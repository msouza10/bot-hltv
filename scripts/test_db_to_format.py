#!/usr/bin/env python3
"""
Test: Simular o fluxo de buscar streams do DB e formatar
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import format_streams_field


async def test_db_to_format():
    """Test: Buscar do DB e formatar"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Buscar streams do DB e formatar")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    
    # Buscar um match com streams
    match_id = 1269342  # Sabemos que tem streams
    
    print(f"1️⃣  Buscando streams do DB para match {match_id}...")
    streams = await cache_mgr.get_match_streams(match_id)
    
    print(f"   ✅ {len(streams)} streams recuperados\n")
    
    if streams:
        print(f"2️⃣  Raw streams (do DB):")
        for i, s in enumerate(streams):
            print(f"   Stream {i}:")
            for k, v in s.items():
                print(f"      {k}: {v} (type: {type(v).__name__})")
        
        print(f"\n3️⃣  Formatando com format_streams_field()...")
        formatted = format_streams_field(streams)
        
        print(f"   Resultado:\n")
        if formatted:
            for line in formatted.split("\n"):
                print(f"   {line}")
        else:
            print(f"   ❌ Nenhum resultado (None)")
    
    print("\n" + "="*80 + "\n")


async def main():
    try:
        await test_db_to_format()
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
