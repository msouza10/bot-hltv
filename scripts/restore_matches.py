#!/usr/bin/env python3
"""
✅ Script para restaurar as partidas da API ao cache
Busca as partidas finished e as armazena no banco
"""

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.database.cache_manager import MatchCacheManager
from src.services.pandascore_service import PandaScoreClient

async def restore_matches():
    """Restaurar as 5 partidas ao banco de dados"""
    
    db_url = "file:./data/bot.db"
    cache_manager = MatchCacheManager(db_url)
    api_client = PandaScoreClient()
    
    print("\n" + "="*70)
    print("✅ RESTAURAR PARTIDAS AO CACHE")
    print("="*70)
    
    target_ids = [1261044, 1264834, 1269192, 1269213, 1269174]
    
    try:
        print(f"\n🔍 Buscando {len(target_ids)} partidas na API...")
        
        # Buscar as partidas das 3 primeiras páginas
        finished_matches = []
        for page in range(1, 4):
            page_matches = await api_client.get_past_matches(per_page=100, page=page)
            finished_matches.extend(page_matches)
            if not page_matches:
                break
        
        # Filtrar apenas as que queremos
        matches_to_restore = [m for m in finished_matches if m['id'] in target_ids]
        
        print(f"✅ Encontradas: {len(matches_to_restore)} partidas")
        
        # Restaurar ao cache
        print(f"\n💾 Armazenando no banco de dados...")
        for match in matches_to_restore:
            await cache_manager.cache_matches([match], "restore")
            print(f"   ✅ {match.get('id')}: {match.get('name')}")
        
        print(f"\n✅ RESTAURAÇÃO CONCLUÍDA")
        print(f"   Total: {len(matches_to_restore)} partidas restauradas")
        
    finally:
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(restore_matches())
