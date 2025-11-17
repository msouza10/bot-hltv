#!/usr/bin/env python3
"""
Debug: Inspecionar o que está salvo na tabela match_streams
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


async def inspect_db():
    """Ver o que está salvo no banco"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: Conteúdo da tabela match_streams")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    
    try:
        client = await cache_mgr.get_client()
        
        # Buscar tudo
        result = await client.execute("SELECT COUNT(*) FROM match_streams")
        count = result.rows[0][0] if result.rows else 0
        
        print(f"1️⃣  Total de streams no DB: {count}\n")
        
        if count == 0:
            print("   ⚠️  Nenhum stream no banco!\n")
            return
        
        # Mostrar primeiros 10
        print(f"2️⃣  Primeiros 10 streams:\n")
        
        result = await client.execute("""
            SELECT match_id, platform, channel_name, language, is_official, is_main, raw_url
            FROM match_streams
            LIMIT 10
        """)
        
        for row in result.rows:
            match_id = row[0]
            platform = row[1]
            channel_name = row[2]
            language = row[3]
            is_official = row[4]
            is_main = row[5]
            raw_url = row[6]
            
            print(f"  Match {match_id}:")
            print(f"    Platform: {platform}")
            print(f"    Channel: {channel_name}")
            print(f"    Language: {language}")
            print(f"    Official: {is_official}")
            print(f"    Main: {is_main}")
            print(f"    URL: {raw_url}")
            print()
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()


async def main():
    await inspect_db()


if __name__ == "__main__":
    asyncio.run(main())
