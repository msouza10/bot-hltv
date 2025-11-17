#!/usr/bin/env python3
"""
Script para popular retroativamente streams de matches que já estão em cache.
Executa uma única vez para sincronizar streams de matches antigos.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import json

sys.path.insert(0, str(Path.cwd()))
load_dotenv()

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager

async def sync_streams():
    api = PandaScoreClient()
    cache = MatchCacheManager('file:./data/bot.db')
    
    print("=" * 80)
    print("🔄 SINCRONIZANDO STREAMS DE MATCHES EM CACHE")
    print("=" * 80)
    
    client = await cache.get_client()
    
    # 1. Contar matches sem streams
    print("\n[1] 📊 Analisando matches em cache...")
    
    result = await client.execute(
        """SELECT COUNT(*) FROM matches_cache"""
    )
    total_matches = result.rows[0][0] if result.rows else 0
    print(f"    Total de matches em cache: {total_matches}")
    
    result = await client.execute(
        """SELECT COUNT(DISTINCT match_id) FROM match_streams"""
    )
    matches_with_streams = result.rows[0][0] if result.rows else 0
    print(f"    Matches com streams cacheadas: {matches_with_streams}")
    print(f"    Matches SEM streams cacheadas: {total_matches - matches_with_streams}")
    
    # 2. Buscar matches que precisam de sincronização
    print("\n[2] 🔍 Buscando matches ao vivo/futuro para sincronizar...")
    
    result = await client.execute(
        """
        SELECT match_id, match_data 
        FROM matches_cache 
        WHERE status IN ('not_started', 'running')
        ORDER BY begin_at DESC
        """
    )
    
    matches_to_sync = result.rows
    print(f"    Encontrados: {len(matches_to_sync)} matches")
    
    if not matches_to_sync:
        print("\n✓ Nenhum match para sincronizar!")
        return
    
    # 3. Para cada match futuro, tentar buscar streams da API e cachear
    print("\n[3] 🔧 Sincronizando streams da API...")
    
    synced = 0
    errors = 0
    already_cached = 0
    
    for match_id, match_data_json in matches_to_sync:
        try:
            # Verificar se já tem streams
            existing = await cache.get_match_streams(match_id)
            if existing:
                already_cached += 1
                continue
            
            # Buscar da API
            api_match = await api.get_match_details(match_id)
            if not api_match:
                print(f"   ⚠️ Match {match_id}: não encontrado na API")
                continue
            
            streams_list = api_match.get('streams_list', [])
            if not streams_list:
                print(f"   - Match {match_id}: sem streams")
                continue
            
            # Cachear
            success = await cache.cache_streams(match_id, streams_list)
            if success:
                synced += 1
                print(f"   ✓ Match {match_id}: {len(streams_list)} stream(s) cacheada(s)")
            else:
                errors += 1
                print(f"   ✗ Match {match_id}: erro ao cachear")
        
        except Exception as e:
            errors += 1
            print(f"   ✗ Match {match_id}: {e}")
    
    print("\n" + "=" * 80)
    print("📊 RESULTADO DA SINCRONIZAÇÃO")
    print("=" * 80)
    print(f"✓ Novos matches sincronizados: {synced}")
    print(f"✓ Matches já com streams: {already_cached}")
    print(f"✗ Erros: {errors}")
    print(f"📈 Total sincronizado agora: {matches_with_streams + synced}")
    
    await api.close()
    await cache.close()

asyncio.run(sync_streams())
