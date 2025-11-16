#!/usr/bin/env python3
"""
🧹 Script para limpar partidas que não existem mais na API
Essas partidas "fantasma" ficam travadas em running eternamente
"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.database.cache_manager import MatchCacheManager
from src.services.pandascore_service import PandaScoreClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def cleanup_ghost_matches():
    """Remove partidas que não existem mais na API"""
    
    db_url = "file:./data/bot.db"
    cache_manager = MatchCacheManager(db_url)
    api_client = PandaScoreClient()
    
    print("\n" + "="*70)
    print("🧹 LIMPEZA DE PARTIDAS FANTASMA")
    print("="*70)
    
    try:
        client = await cache_manager.get_client()
        
        # 1. Buscar TODAS as partidas em running
        result = await client.execute("""
            SELECT match_id, match_data, updated_at, cached_at
            FROM matches_cache
            WHERE status = 'running'
            ORDER BY updated_at DESC
        """)
        
        running_matches = result.rows if result.rows else []
        print(f"\n📊 Partidas em running no banco: {len(running_matches)}")
        
        if not running_matches:
            print("✅ Nenhuma partida em running")
            return
        
        # 2. Verificar quais existem na API
        all_running = await api_client.get_running_matches()
        valid_ids = {m['id'] for m in all_running}
        
        print(f"🔴 Partidas running na API PandaScore: {len(all_running)}")
        print(f"   IDs: {sorted(valid_ids)}")
        
        # 3. Encontrar fantasmas (em running local mas não na API)
        ghosts = []
        for match_id, match_data, updated_at, cached_at in running_matches:
            if match_id not in valid_ids:
                ghosts.append((match_id, match_data, updated_at, cached_at))
        
        if not ghosts:
            print("\n✅ Nenhuma partida fantasma encontrada!")
            return
        
        print(f"\n🚨 PARTIDAS FANTASMA ENCONTRADAS: {len(ghosts)}")
        print("-"*70)
        
        for match_id, match_data, updated_at, cached_at in ghosts:
            import json
            data = json.loads(match_data)
            name = data.get('name', 'SEM NOME')
            print(f"❌ ID {match_id}: {name}")
            print(f"   Cached: {cached_at}")
            print(f"   Atualizada: {updated_at}")
        
        # 4. Perguntar antes de deletar
        print(f"\n⚠️  DELETAR {len(ghosts)} PARTIDA(S) FANTASMA?")
        response = input("Confirmar (s/n)? ").strip().lower()
        
        if response != 's':
            print("❌ Operação cancelada")
            return
        
        # 5. Deletar
        deleted = 0
        for match_id, _, _, _ in ghosts:
            try:
                await client.execute(f"""
                    DELETE FROM matches_cache
                    WHERE match_id = {match_id}
                """)
                deleted += 1
                print(f"✅ Deletado: {match_id}")
            except Exception as e:
                print(f"❌ Erro ao deletar {match_id}: {e}")
        
        print(f"\n🎉 LIMPEZA CONCLUÍDA")
        print(f"   Deletados: {deleted}/{len(ghosts)} partidas fantasma")
        
    finally:
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_ghost_matches())
