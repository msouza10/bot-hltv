#!/usr/bin/env python3
"""
Simula exatamente o que acontece no comando /aovivo:
1. Cache scheduler atualiza matches (cachea streams)
2. Usuário executa /aovivo
3. Comando recupera matches do cache
4. Augmenta com streams
5. Mostra em embed
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
from src.utils.embeds import augment_match_with_streams, create_match_embed

async def simulate_aovivo_command():
    api = PandaScoreClient()
    cache = MatchCacheManager('file:./data/bot.db')
    
    print("=" * 80)
    print("🧪 SIMULAÇÃO: Comando /aovivo")
    print("=" * 80)
    
    # STAGE 1: Cache scheduler updates (como cache_scheduler.update_live_matches faz)
    print("\n[STAGE 1] 🔄 Cache Scheduler Updates Running Matches...")
    print("          (como cache_scheduler.py executa a cada 5 minutos)")
    
    running = await api.get_running_matches()
    if not running:
        print("⚠️ Nenhum match ao vivo")
        return
    
    print(f"✓ API retornou {len(running)} matches")
    
    # Simular o que cache_matches faz - cachear cada match
    print("✓ Cacheando matches com cache_manager.cache_matches()...")
    await cache.cache_matches(running, "running")
    
    # STAGE 2: User executes /aovivo command
    print("\n[STAGE 2] 💬 User executes /aovivo command...")
    
    # Recuperar do cache (COMO O COMANDO FARIA)
    # Nota: get_cached_matches retorna matches DO BANCO, sem streams_list
    client = await cache.get_client()
    result = await client.execute(
        """SELECT match_data FROM matches_cache 
           WHERE status = 'running' LIMIT 5"""
    )
    
    cached_matches_from_db = []
    for row in result.rows:
        try:
            match_json = row[0]
            match = json.loads(match_json)
            cached_matches_from_db.append(match)
        except:
            pass
    
    print(f"✓ Recuperou {len(cached_matches_from_db)} matches DO BANCO")
    print(f"✓ Matches têm 'streams_list'? {any('streams_list' in m for m in cached_matches_from_db)}")
    
    # STAGE 3: Augment and display
    print("\n[STAGE 3] 🎨 Augmenting with streams and creating embeds...")
    
    embeds = []
    for i, match in enumerate(cached_matches_from_db[:5], 1):
        try:
            # THIS IS THE KEY PART - augment_match_with_streams
            augmented = await augment_match_with_streams(match, cache)
            
            has_streams = 'formatted_streams' in augmented
            
            print(f"\n  Match {i}:")
            team1 = match.get('opponents', [{}])[0].get('opponent', {}).get('name', '?')
            team2 = match.get('opponents', [{}])[1].get('opponent', {}).get('name', '?') if len(match.get('opponents', [])) > 1 else '?'
            print(f"    {team1} vs {team2}")
            print(f"    Tem streams formatadas? {'✓' if has_streams else '✗'}")
            
            if has_streams:
                print(f"    Conteúdo:")
                for line in augmented['formatted_streams'].split('\n'):
                    print(f"      {line}")
            
            # Create embed
            embed = create_match_embed(augmented)
            embeds.append(embed)
            
            # Check if streams field is in embed
            has_streams_field = any(f.name == "📡 Streams" for f in embed.fields)
            print(f"    Embed tem campo 📡 Streams? {'✓' if has_streams_field else '✗'}")
            
        except Exception as e:
            print(f"  ✗ Erro ao processar match: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"✅ RESULTADO: {len(embeds)} embeds criados com sucesso")
    print("=" * 80)
    
    # Contar quantos têm streams
    embeds_with_streams = sum(1 for e in embeds if any(f.name == "📡 Streams" for f in e.fields))
    print(f"\n📊 Embeds com campo Streams: {embeds_with_streams}/{len(embeds)}")
    
    if embeds_with_streams == len(embeds):
        print("\n🎉 SUCESSO TOTAL! Todos os embeds têm streams!")
    elif embeds_with_streams > 0:
        print(f"\n⚠️ Parcial: {embeds_with_streams} de {len(embeds)} embeds têm streams")
    else:
        print("\n❌ PROBLEMA: Nenhum embed tem streams")
    
    await api.close()
    await cache.close()

asyncio.run(simulate_aovivo_command())
