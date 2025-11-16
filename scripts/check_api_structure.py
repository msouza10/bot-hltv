#!/usr/bin/env python3
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

from src.services.pandascore_service import PandaScoreClient

async def check_api():
    client = PandaScoreClient(os.getenv("PANDASCORE_API_KEY"))
    
    print("=== CHECANDO ESTRUTURA DE PARTIDA FINISHED ===")
    matches = await client.get_past_matches(per_page=1)
    
    if matches:
        match = matches[0]
        print(f"\nMatch ID: {match.get('id')}")
        print(f"Status: {match.get('status')}")
        print(f"Begin: {match.get('begin_at')}")
        print(f"End: {match.get('end_at')}")
        print(f"Scheduled: {match.get('scheduled_at')}")
        print(f"\nFields disponíveis: {list(match.keys())}")
        print(f"\nResultados: {match.get('results')}")
    
    await client.close()

asyncio.run(check_api())
