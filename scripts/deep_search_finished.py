#!/usr/bin/env python3
"""
🔍 Busca profunda: Procurar partidas em finished com pagination completa
"""

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.services.pandascore_service import PandaScoreClient

async def deep_search():
    api = PandaScoreClient()
    
    target_ids = [1261044, 1264834, 1269192, 1269213, 1269174]
    
    print("\n" + "="*70)
    print("🔍 BUSCA PROFUNDA: PAGINATION COMPLETA")
    print("="*70)
    
    found_matches = {}
    page = 1
    total_checked = 0
    
    # Buscar com pagination - cada página tem 100 resultados
    while True:
        print(f"\n📄 Página {page} (resultados {total_checked + 1} a {total_checked + 100})...")
        
        try:
            params = {
                "filter[status]": "finished",
                "sort": "-end_at",
                "per_page": 100,
                "page": page
            }
            
            # Fazer requisição manual para ter controle sobre pagination
            import aiohttp
            session = await api._get_session()
            url = f"https://api.pandascore.co/csgo/matches/past"
            
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                
                if not data or len(data) == 0:
                    print(f"   ✅ Fim da lista. Total verificado: {total_checked}")
                    break
                
                # Procurar os IDs nesta página
                page_found = 0
                for match in data:
                    match_id = match['id']
                    if match_id in target_ids:
                        found_matches[match_id] = match
                        page_found += 1
                
                if page_found > 0:
                    print(f"   ✅ {page_found} partida(s) encontrada(s) nesta página!")
                    for match_id, match in found_matches.items():
                        print(f"      - ID {match_id}: {match.get('name')} | Status: {match.get('status')} | Score: {match.get('results', [])}")
                else:
                    print(f"   ❌ Nenhuma encontrada nesta página ({len(data)} partidas)")
                
                total_checked += len(data)
                
                # Se encontrou todas, parar
                if len(found_matches) == len(target_ids):
                    print(f"\n🎉 TODAS AS {len(target_ids)} PARTIDAS ENCONTRADAS!")
                    break
                
                page += 1
                
                # Limite de segurança para não fazer muitas requisições
                if page > 50:
                    print(f"\n⚠️  Atingido limite de 50 páginas ({total_checked} partidas verificadas)")
                    break
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            break
    
    print("\n" + "="*70)
    print("📊 RESUMO DOS RESULTADOS")
    print("="*70)
    
    print(f"\nTotal de partidas verificadas: {total_checked}")
    print(f"Partidas encontradas: {len(found_matches)}/{len(target_ids)}")
    
    if found_matches:
        print("\n✅ PARTIDAS ENCONTRADAS:")
        for match_id, match in found_matches.items():
            print(f"\n🎮 ID {match_id}")
            print(f"   Nome: {match.get('name')}")
            print(f"   Status: {match.get('status')}")
            print(f"   Resultado: {match.get('results', [])}")
            print(f"   Fim: {match.get('end_at')}")
            print(f"   Tournament: {match.get('tournament', {}).get('name', 'N/A')}")
    
    not_found = [id for id in target_ids if id not in found_matches]
    if not_found:
        print(f"\n❌ PARTIDAS NÃO ENCONTRADAS:")
        for match_id in not_found:
            print(f"   - ID {match_id}")
    
    await api.close()

asyncio.run(deep_search())
