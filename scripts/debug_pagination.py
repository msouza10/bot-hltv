#!/usr/bin/env python3
"""
Debug: Verificar o que get_past_matches retorna
"""

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.services.pandascore_service import PandaScoreClient

async def debug():
    api = PandaScoreClient()
    
    print("\n" + "="*70)
    print("DEBUG: O que get_past_matches retorna?")
    print("="*70)
    
    finished = await api.get_past_matches(per_page=100)
    
    print(f"\nTotal de partidas: {len(finished)}")
    print("\nPrimeiras 10 partidas:")
    for i, m in enumerate(finished[:10]):
        print(f"{i+1}. ID {m['id']}: {m.get('name')} | end_at: {m.get('end_at')}")
    
    print("\nÚltimas 10 partidas:")
    for i, m in enumerate(finished[-10:], start=len(finished)-9):
        print(f"{i}. ID {m['id']}: {m.get('name')} | end_at: {m.get('end_at')}")
    
    # Procurar a maior página que retorna
    print("\n" + "-"*70)
    print("Testando pagination direto...")
    
    import aiohttp
    session = await api._get_session()
    
    for page in [1, 2, 3]:
        params = {
            "filter[status]": "finished",
            "sort": "-end_at",
            "per_page": 100,
            "page": page
        }
        
        async with session.get("https://api.pandascore.co/csgo/matches/past", params=params) as resp:
            data = await resp.json()
            print(f"\nPágina {page}: {len(data)} partidas")
            if data:
                target_ids = [1261044, 1264834, 1269192, 1269213, 1269174]
                found_in_page = [m['id'] for m in data if m['id'] in target_ids]
                if found_in_page:
                    print(f"   🎯 Encontrados: {found_in_page}")
    
    await api.close()

asyncio.run(debug())
