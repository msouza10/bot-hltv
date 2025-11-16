#!/usr/bin/env python3
"""
🧪 Teste detalhado do status das partidas na API
"""
import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import asyncio
from src.services.pandascore_service import PandaScoreClient
from dotenv import load_dotenv
import os

load_dotenv()

async def test_match_status():
    api = PandaScoreClient()
    
    match_ids = [1261044, 1264834, 1269192, 1269213]
    
    print("\n" + "="*70)
    print("🔍 VERIFICANDO STATUS DAS PARTIDAS NA API")
    print("="*70)
    
    for match_id in match_ids:
        print(f"\n📍 Match ID: {match_id}")
        
        # Buscar em finished
        try:
            finished = await api.get_past_matches(hours=24, per_page=100)
            match = next((m for m in finished if m['id'] == match_id), None)
            if match:
                print(f"   ✅ ENCONTRADO em finished")
                print(f"      Status: {match.get('status')}")
                print(f"      Results: {match.get('results', 'N/A')}")
                print(f"      Winner: {match.get('winner_type', 'N/A')}")
                print(f"      End at: {match.get('end_at', 'N/A')}")
                continue
        except Exception as e:
            print(f"   Erro ao buscar finished: {e}")
        
        # Buscar em running
        try:
            running = await api.get_running_matches()
            match = next((m for m in running if m['id'] == match_id), None)
            if match:
                print(f"   🔴 ENCONTRADO em running")
                print(f"      Status: {match.get('status')}")
                print(f"      Live Score: {match.get('live_score', 'N/A')}")
                continue
        except Exception as e:
            print(f"   Erro ao buscar running: {e}")
        
        print(f"   ❌ NÃO ENCONTRADO em nenhum endpoint")
    
    await api.close()

asyncio.run(test_match_status())
