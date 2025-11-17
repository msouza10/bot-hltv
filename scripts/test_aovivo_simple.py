#!/usr/bin/env python3
"""
Teste simples e direto: verifica que quando /aovivo é executado,
streams aparecem nos embeds.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path.cwd()))
load_dotenv()

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed
import json

async def test():
    api = PandaScoreClient()
    cache = MatchCacheManager('file:./data/bot.db')
    
    print("=" * 80)
    print("✅ TESTE: Streams aparecem no /aovivo")
    print("=" * 80)
    
    # 1. Buscar match da API
    print("\n[1] Buscando match da API...")
    running = await api.get_running_matches()
    
    if not running:
        print("❌ Nenhum match ao vivo")
        return False
    
    match = running[0]
    mid = match.get('id')
    team1 = match.get('opponents', [{}])[0].get('opponent', {}).get('name', '?')
    team2 = match.get('opponents', [{}])[1].get('opponent', {}).get('name', '?') if len(match.get('opponents', [])) > 1 else '?'
    
    print(f"✓ {team1} vs {team2}")
    print(f"✓ Streams na API: {len(match.get('streams_list', []))}")
    
    # 2. Cachear
    print("\n[2] Cacheando streams...")
    await cache.cache_streams(mid, match.get('streams_list', []))
    print("✓ Cacheado")
    
    # 3. Simular match do cache (SEM streams_list, como vem do banco)
    print("\n[3] Removendo streams_list (simular match do cache)...")
    cached_match = {k: v for k, v in match.items() if k != 'streams_list'}
    print(f"✓ Tem streams_list? {'streams_list' in cached_match}")
    
    # 4. Augmentar
    print("\n[4] Augmentando com augment_match_with_streams()...")
    augmented = await augment_match_with_streams(cached_match, cache)
    print(f"✓ Tem 'formatted_streams'? {'formatted_streams' in augmented}")
    
    if 'formatted_streams' in augmented:
        print(f"\n   Conteúdo:")
        for line in augmented['formatted_streams'].split('\n'):
            print(f"   {line}")
    
    # 5. Criar embed
    print("\n[5] Criando embed...")
    embed = create_match_embed(augmented)
    
    has_streams_field = any(f.name == "📡 Streams" for f in embed.fields)
    print(f"✓ Embed tem campo '📡 Streams'? {has_streams_field}")
    
    print("\n" + "=" * 80)
    if has_streams_field and 'formatted_streams' in augmented:
        print("✅ SUCESSO! Streams aparecerão no comando /aovivo")
        print("=" * 80)
        result = True
    else:
        print("❌ PROBLEMA! Streams não aparecerão")
        print("=" * 80)
        result = False
    
    await api.close()
    await cache.close()
    return result

result = asyncio.run(test())
exit(0 if result else 1)
