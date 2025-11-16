#!/usr/bin/env python3
"""Test to understand the actual status values returned by PandaScore API"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.services.pandascore_service import PandaScoreClient

async def test():
    api = PandaScoreClient()
    
    print("\n" + "="*70)
    print("🔍 TESTANDO ESTATUSES DE PARTIDAS NA API")
    print("="*70)
    
    # Buscar TODOS os finished
    print("\n1️⃣ Buscando últimos 100 finished...")
    finished = await api.get_past_matches(per_page=100)
    print(f"Encontrados: {len(finished)} partidas finished")
    if finished:
        print("   Estatuses únicos nos primeiros 5:")
        for m in finished[:5]:
            print(f"   - ID {m['id']}: {m.get('status')} | Name: {m.get('name')}")
    
    # Buscar running
    print("\n2️⃣ Buscando running matches...")
    running = await api.get_running_matches()
    print(f"Encontrados: {len(running)} partidas running")
    if running:
        for m in running[:3]:
            print(f"   - ID {m['id']}: {m.get('status')} | Name: {m.get('name')}")
    
    # Buscar canceladas
    print("\n3️⃣ Buscando canceled matches...")
    canceled = await api.get_canceled_matches(per_page=100)
    print(f"Encontrados: {len(canceled)} partidas canceled/postponed")
    if canceled:
        for m in canceled[:3]:
            print(f"   - ID {m['id']}: {m.get('status')} | Name: {m.get('name')}")
    
    # Agora procurar as IDs específicas
    print("\n" + "="*70)
    print("🎯 PROCURANDO IDS ESPECÍFICAS")
    print("="*70)
    
    target_ids = [1261044, 1264834, 1269192, 1269213]
    
    for target_id in target_ids:
        found = False
        
        # Procurar em finished
        match = next((m for m in finished if m['id'] == target_id), None)
        if match:
            print(f"✅ ID {target_id}: ENCONTRADO em finished | Status: {match.get('status')}")
            found = True
        
        # Procurar em running
        match = next((m for m in running if m['id'] == target_id), None)
        if match:
            print(f"🔴 ID {target_id}: ENCONTRADO em running | Status: {match.get('status')}")
            found = True
        
        # Procurar em canceled
        match = next((m for m in canceled if m['id'] == target_id), None)
        if match:
            print(f"🚫 ID {target_id}: ENCONTRADO em canceled | Status: {match.get('status')}")
            found = True
        
        if not found:
            print(f"❌ ID {target_id}: NÃO ENCONTRADO em nenhum lugar")
    
    await api.close()

asyncio.run(test())
