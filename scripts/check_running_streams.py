#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path.cwd()))
load_dotenv()

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import format_streams_field, augment_match_with_streams
import json

async def check():
    api = PandaScoreClient()
    cache = MatchCacheManager('file:./data/bot.db')
    
    print("=" * 80)
    print("🔍 VERIFICANDO STREAMS EM MATCHES AO VIVO")
    print("=" * 80)
    
    # Buscar running matches
    running = await api.get_running_matches()
    print(f"\n📊 Running matches da API: {len(running)}")
    
    if not running:
        print("⚠️ Nenhum match ao vivo encontrado")
    else:
        m = running[0]
        mid = m.get('id')
        team1 = m.get('opponents', [{}])[0].get('opponent', {}).get('name', '?')
        team2 = m.get('opponents', [{}])[1].get('opponent', {}).get('name', '?') if len(m.get('opponents', [])) > 1 else '?'
        
        print(f"\n🎮 Primeiro match: {team1} vs {team2} (ID: {mid})")
        print(f"\n📡 Streams na RESPOSTA DA API:")
        streams_list = m.get('streams_list', [])
        print(f"   Total: {len(streams_list)}")
        
        if streams_list:
            for s in streams_list:
                print(f"   - {s.get('raw_url')} ({s.get('language')}) - Official: {s.get('official')}")
        else:
            print("   ⚠️ Sem streams na API!")
        
        # Checar cache
        print(f"\n💾 Verificando CACHE para match {mid}:")
        cached = await cache.get_match_streams(mid)
        print(f"   Total cacheado: {len(cached)}")
        
        if cached:
            for s in cached:
                print(f"   - {s['platform']} / {s['channel_name']} ({s['language']}) - Official: {s['is_official']}")
        else:
            print("   ⚠️ Sem streams em cache!")
            
            # Tentar cachear agora
            print(f"\n   🔧 Tentando cachear streams_list agora...")
            if streams_list:
                success = await cache.cache_streams(mid, streams_list)
                print(f"   Resultado: {'✅ Sucesso' if success else '❌ Falha'}")
                
                # Verificar novamente
                cached = await cache.get_match_streams(mid)
                print(f"   Cache agora: {len(cached)} streams")
        
        # Testar formatação
        if cached:
            print(f"\n🎨 Formatação para embed:")
            formatted = format_streams_field(cached)
            if formatted:
                for line in formatted.split('\n'):
                    print(f"   {line}")
    
    await api.close()
    await cache.close()

asyncio.run(check())
