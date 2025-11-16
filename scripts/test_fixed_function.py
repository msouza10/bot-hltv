#!/usr/bin/env python3
"""
✅ Teste: Verificar se a função corrigida encontra as partidas finished
"""

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.services.pandascore_service import PandaScoreClient

async def test_fixed_function():
    api = PandaScoreClient()
    
    target_ids = [1261044, 1264834, 1269192, 1269213, 1269174]
    
    print("\n" + "="*70)
    print("✅ TESTE: Função get_past_matches() COM PAGINATION")
    print("="*70)
    
    print("\n🔍 Buscando últimas partidas finished (com pagination - 3 páginas)...")
    finished = []
    
    # Buscar múltiplas páginas como faz o cache_scheduler
    for page in range(1, 4):
        page_matches = await api.get_past_matches(per_page=100, page=page)
        finished.extend(page_matches)
        print(f"   Página {page}: {len(page_matches)} partidas")
        if not page_matches:
            break
    
    print(f"\nTotal de partidas retornadas: {len(finished)}")
    
    found = {}
    for match_id in target_ids:
        match = next((m for m in finished if m['id'] == match_id), None)
        if match:
            found[match_id] = match
            print(f"✅ ID {match_id}: {match.get('name')} - Status: {match.get('status')}")
        else:
            print(f"❌ ID {match_id}: NÃO ENCONTRADO")
    
    print(f"\n📊 Resultado: {len(found)}/{len(target_ids)} partidas encontradas")
    
    if len(found) == len(target_ids):
        print("✅ SUCESSO! A função corrigida encontra TODAS as partidas!")
    else:
        print("⚠️  Algumas partidas ainda não foram encontradas")
    
    await api.close()

asyncio.run(test_fixed_function())
