#!/usr/bin/env python3
import asyncio
import json
from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()

async def check_api_with_status():
    api_key = os.getenv("PANDASCORE_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("=== TESTANDO DIFERENTES FILTROS ===\n")
        
        # Teste 1: /csgo/matches/past sem filtro (atual)
        print("1. GET /csgo/matches/past (sem filtro)")
        async with session.get("https://api.pandascore.co/csgo/matches/past", 
                              params={"per_page": 5, "sort": "-end_at"}) as r:
            data = await r.json()
            print(f"   Resultado: {len(data)} partidas")
            for match in data:
                print(f"   - ID: {match['id']}, Status: {match['status']}, End: {match.get('end_at')}")
        
        # Teste 2: Filtrar por status=finished
        print("\n2. GET /csgo/matches/past com filter[status]=finished")
        async with session.get("https://api.pandascore.co/csgo/matches/past",
                              params={"filter[status]": "finished", "per_page": 5, "sort": "-end_at"}) as r:
            data = await r.json()
            print(f"   Resultado: {len(data)} partidas")
            for match in data[:5]:
                print(f"   - ID: {match['id']}, Status: {match['status']}, End: {match.get('end_at')}")
        
        # Teste 3: Usando endpoint /csgo/matches com status
        print("\n3. GET /csgo/matches com filter[status]=finished")
        async with session.get("https://api.pandascore.co/csgo/matches",
                              params={"filter[status]": "finished", "per_page": 5, "sort": "-end_at"}) as r:
            data = await r.json()
            print(f"   Resultado: {len(data)} partidas")
            for match in data[:5]:
                print(f"   - ID: {match['id']}, Status: {match['status']}, End: {match.get('end_at')}")

asyncio.run(check_api_with_status())
