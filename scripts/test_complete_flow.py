#!/usr/bin/env python3
"""
Teste simulando o fluxo completo:
1. API retorna match com streams_list
2. Cache armazena
3. Comando /aovivo recupera do cache e mostra streams
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
from src.utils.embeds import augment_match_with_streams, format_streams_field, create_match_embed
import json

async def test_flow():
    api = PandaScoreClient()
    cache = MatchCacheManager('file:./data/bot.db')
    
    print("=" * 80)
    print("🧪 TESTE: Fluxo Completo de Streams")
    print("=" * 80)
    
    # 1. Obter match da API (com streams_list)
    print("\n[1] 📥 Buscando running match DA API...")
    running = await api.get_running_matches()
    if not running:
        print("❌ Nenhum match ao vivo")
        return
    
    api_match = running[0]
    match_id = api_match.get('id')
    team1 = api_match.get('opponents', [{}])[0].get('opponent', {}).get('name', '?')
    team2 = api_match.get('opponents', [{}])[1].get('opponent', {}).get('name', '?') if len(api_match.get('opponents', [])) > 1 else '?'
    
    print(f"✓ Match: {team1} vs {team2} (ID: {match_id})")
    print(f"✓ Streams na resposta: {len(api_match.get('streams_list', []))}")
    
    # 2. Simular que o match foi recuperado do CACHE (sem streams_list)
    print("\n[2] 💾 Simulando retrieval do CACHE (sem streams_list)...")
    cached_match = {
        'id': match_id,
        'opponents': api_match.get('opponents'),
        'league': api_match.get('league'),
        'tournament': api_match.get('tournament'),
        'status': api_match.get('status'),
        'begin_at': api_match.get('begin_at'),
        'scheduled_at': api_match.get('scheduled_at'),
        'number_of_games': api_match.get('number_of_games'),
        # ⚠️ Note: SEM streams_list!
    }
    print(f"✓ Match do cache: tem 'streams_list'? {('streams_list' in cached_match)}")
    
    # 3. Augmentar match do cache
    print("\n[3] 🔧 Augmentando match com augment_match_with_streams()...")
    
    # 3a. Verificar se tem streams em cache
    print("   a) Checando se tem streams cacheadas...")
    existing_streams = await cache.get_match_streams(match_id)
    print(f"      Streams já em cache: {len(existing_streams)}")
    
    # 3b. Agora a magic: augment_match tenta buscar do cache
    #     mas como nós testamos, não encontrará nada se não foi cacheado antes
    print("   b) Augmentando (sem streams_list no match)...")
    augmented = await augment_match_with_streams(cached_match, cache)
    
    has_formatted = 'formatted_streams' in augmented
    print(f"      Tem 'formatted_streams'? {has_formatted}")
    
    if has_formatted:
        print(f"\n      ✓ Conteúdo:")
        for line in augmented['formatted_streams'].split('\n'):
            print(f"        {line}")
    else:
        print(f"      ⚠️ Sem streams! Problema detectado.")
    
    # 4. Agora teste com streams_list (como vem da API)
    print("\n[4] 🔧 Augmentando match COM streams_list (como da API)...")
    api_match_copy = api_match.copy()
    
    print("   a) Cleanando cache antes...")
    # Limpar cache para simular cenário novo
    client = await cache.get_client()
    await client.execute("DELETE FROM match_streams WHERE match_id = ?", [match_id])
    print("      Cache limpo")
    
    print("   b) Augmentando COM streams_list...")
    augmented2 = await augment_match_with_streams(api_match_copy, cache)
    
    has_formatted2 = 'formatted_streams' in augmented2
    print(f"      Tem 'formatted_streams'? {has_formatted2}")
    
    if has_formatted2:
        print(f"\n      ✓ Conteúdo:")
        for line in augmented2['formatted_streams'].split('\n'):
            print(f"        {line}")
    
    # 5. Teste completo do embed
    print("\n[5] 🎨 Gerando embed completo...")
    embed = create_match_embed(augmented2)
    print(f"✓ Embed criado com sucesso")
    print(f"  Title: {embed.title}")
    print(f"  Fields: {len(embed.fields)}")
    
    for i, field in enumerate(embed.fields):
        print(f"    {i+1}. {field.name}")
        if field.name == "📡 Streams":
            print(f"       ✓ Campo de streams presente!")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)
    
    await api.close()
    await cache.close()

asyncio.run(test_flow())
