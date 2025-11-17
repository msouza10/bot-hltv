#!/usr/bin/env python3
"""
Forçar uma atualização manual do cache para testar se funciona
"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
import os
from dotenv import load_dotenv

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager

async def force_cache_update():
    """Força uma atualização manual do cache"""
    
    load_dotenv()
    
    api_key = os.getenv("PANDASCORE_API_KEY")
    libsql_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    
    api_client = PandaScoreClient(api_key)
    cache_manager = MatchCacheManager(libsql_url)
    
    try:
        print("=" * 80)
        print("🔄 FORÇANDO ATUALIZAÇÃO MANUAL DO CACHE")
        print("=" * 80)
        print()
        
        # Atualizar partidas próximas
        print("1️⃣  Buscando partidas próximas...")
        upcoming = await api_client.get_upcoming_matches(per_page=50)
        print(f"   ✅ {len(upcoming)} partidas próximas obtidas")
        
        if upcoming:
            stats = await cache_manager.cache_matches(upcoming, "not_started")
            print(f"   📊 Cache atualizado: {stats['added']} novas, {stats['updated']} atualizadas")
        
        # Atualizar partidas ao vivo
        print("\n2️⃣  Buscando partidas ao vivo...")
        running = await api_client.get_running_matches()
        print(f"   ✅ {len(running)} partidas ao vivo obtidas")
        
        if running:
            stats = await cache_manager.cache_matches(running, "running")
            print(f"   📊 Cache atualizado: {stats['added']} novas, {stats['updated']} atualizadas")
        
        # Atualizar partidas finalizadas
        print("\n3️⃣  Buscando partidas finalizadas...")
        finished = await api_client.get_past_matches(hours=24, per_page=20)
        print(f"   ✅ {len(finished)} partidas finalizadas obtidas")
        
        if finished:
            stats = await cache_manager.cache_matches(finished, "finished")
            print(f"   📊 Cache atualizado: {stats['added']} novas, {stats['updated']} atualizadas")
        
        # Verificar novo estado
        print("\n" + "=" * 80)
        print("📊 NOVO ESTADO DO CACHE")
        print("=" * 80)
        print()
        
        upcoming_cached = await cache_manager.get_cached_matches("not_started", 50)
        running_cached = await cache_manager.get_cached_matches("running", 50)
        finished_cached = await cache_manager.get_cached_matches("finished", 50)
        
        print(f"📅 Upcoming: {len(upcoming_cached)}")
        print(f"🔴 Running: {len(running_cached)}")
        print(f"✅ Finished: {len(finished_cached)}")
        
        await cache_manager.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_cache_update())
