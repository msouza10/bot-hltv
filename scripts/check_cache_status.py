#!/usr/bin/env python3
"""
Verificar se o cache está sendo renovado
"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.database.cache_manager import MatchCacheManager
from datetime import datetime, timedelta

async def check_cache_status():
    """Verifica o status do cache"""
    
    cache_manager = MatchCacheManager(db_url="file:./data/bot.db")
    
    try:
        print("=" * 80)
        print("📊 VERIFICAÇÃO DE STATUS DO CACHE")
        print("=" * 80)
        print()
        
        # Obter todas as partidas em cache
        upcoming = await cache_manager.get_cached_matches("not_started", 50)
        running = await cache_manager.get_cached_matches("running", 50)
        finished = await cache_manager.get_cached_matches("finished", 50)
        
        print(f"📅 UPCOMING (não_iniciadas): {len(upcoming)}")
        if upcoming:
            print(f"   ├─ Primeira: {upcoming[0].get('id')} - {upcoming[0].get('league', {}).get('name', 'N/A')}")
            print(f"   └─ Última: {upcoming[-1].get('id')} - {upcoming[-1].get('league', {}).get('name', 'N/A')}")
        
        print()
        print(f"🔴 RUNNING (ao vivo): {len(running)}")
        if running:
            print(f"   ├─ Primeira: {running[0].get('id')} - {running[0].get('league', {}).get('name', 'N/A')}")
            print(f"   └─ Última: {running[-1].get('id')} - {running[-1].get('league', {}).get('name', 'N/A')}")
        
        print()
        print(f"✅ FINISHED (finalizadas): {len(finished)}")
        if finished:
            print(f"   ├─ Primeira: {finished[0].get('id')} - {finished[0].get('league', {}).get('name', 'N/A')}")
            print(f"   └─ Última: {finished[-1].get('id')} - {finished[-1].get('league', {}).get('name', 'N/A')}")
        
        print()
        print("=" * 80)
        print("🔍 VERIFICANDO TIMESTAMPS DO CACHE")
        print("=" * 80)
        print()
        
        # Verificar quando foi o último update
        client = await cache_manager.get_client()
        result = await client.execute("""
            SELECT MAX(updated_at) as last_update, COUNT(*) as total
            FROM matches_cache
        """)
        
        if result.rows:
            last_update = result.rows[0][0]
            total = result.rows[0][1]
            print(f"📦 Total de registros em cache: {total}")
            print(f"⏱️  Último UPDATE: {last_update}")
            
            if last_update:
                last_update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                now = datetime.now(last_update_time.tzinfo)
                diff = (now - last_update_time).total_seconds() / 60
                print(f"⏳ Tempo desde último update: {diff:.1f} minutos atrás")
                
                if diff > 10:
                    print(f"⚠️  AVISO: Cache não foi atualizado há {diff:.1f} minutos!")
                else:
                    print(f"✅ Cache está fresco (atualizado há {diff:.1f} minutos)")
        
        print()
        print("=" * 80)
        print("🔍 ÚLTIMAS ATUALIZAÇÕES POR STATUS")
        print("=" * 80)
        print()
        
        for status in ["not_started", "running", "finished"]:
            result = await client.execute(f"""
                SELECT COUNT(*) as count, MAX(updated_at) as last_update
                FROM matches_cache
                WHERE status = ?
            """, [status])
            
            if result.rows:
                count = result.rows[0][0]
                last_update = result.rows[0][1]
                print(f"📌 {status.upper()}: {count} matches | Last update: {last_update}")
        
        await cache_manager.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_cache_status())
