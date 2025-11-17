#!/usr/bin/env python3
"""
Teste simples para verificar se a database está respondendo
"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.database.cache_manager import MatchCacheManager

async def test_db():
    cache_mgr = MatchCacheManager(db_url="file:./data/bot.db")
    
    try:
        print("1️⃣  Conectando ao banco...")
        client = await cache_mgr.get_client()
        print("   ✅ Conectado!")
        
        print("\n2️⃣  Executando query simples...")
        result = await asyncio.wait_for(
            client.execute("SELECT COUNT(*) as count FROM matches_cache"),
            timeout=3.0
        )
        print(f"   ✅ Total de matches: {result.rows[0][0]}")
        
        print("\n3️⃣  Tentando inserir teste...")
        import json
        test_match = {
            "id": 9999999,
            "status": "test",
            "begin_at": "2025-11-17T15:00:00Z"
        }
        
        await asyncio.wait_for(
            client.execute("""
                INSERT INTO matches_cache 
                    (match_id, match_data, status, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, [9999999, json.dumps(test_match), "test"]),
            timeout=3.0
        )
        print("   ✅ Inserção funcionou!")
        
        print("\n4️⃣  Limpando...")
        await asyncio.wait_for(
            client.execute("DELETE FROM matches_cache WHERE match_id = ?", [9999999]),
            timeout=3.0
        )
        print("   ✅ Limpeza feita!")
        
        await cache_mgr.close()
        print("\n✅ Teste completou com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
