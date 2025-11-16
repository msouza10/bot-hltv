#!/usr/bin/env python3
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

from src.services.pandascore_service import PandaScoreClient

async def check_api():
    client = PandaScoreClient(os.getenv("PANDASCORE_API_KEY"))
    
    print("=== CONSULTANDO API: PARTIDAS PASSADAS ===")
    matches = await client.get_past_matches(per_page=10)
    
    if matches:
        print(f"\nTotal de partidas retornadas: {len(matches)}")
        print("\nDetalhes das primeiras 5:")
        for match in matches[:5]:
            print(f"\nID: {match.get('id')}")
            print(f"  Status: {match.get('status')}")
            print(f"  Begin: {match.get('begin_at')}")
            print(f"  End: {match.get('end_at')}")
            print(f"  Tournament: {match.get('tournament', {}).get('name')}")
            print(f"  Teams: {match.get('opponents', [{}])[0].get('opponent', {}).get('name', 'N/A')} vs {match.get('opponents', [{}, {}])[1].get('opponent', {}).get('name', 'N/A') if len(match.get('opponents', [])) > 1 else 'N/A'}")
            
            # Verificar se tem resultados
            if match.get('results'):
                print(f"  Results: {match['results']}")
            if match.get('games'):
                print(f"  Games: {len(match['games'])} mapas")
    else:
        print("Nenhuma partida retornada!")
    
    await client.close()

asyncio.run(check_api())
