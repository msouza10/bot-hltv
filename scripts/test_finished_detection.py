#!/usr/bin/env python3
"""
🧪 Teste: Verificar se partidas finished estão sendo detectadas corretamente
Simula a função check_running_to_finished_transitions_fast()
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PANDASCORE_API_KEY')
MATCH_IDS = ['1261044', '1264834', '1269192', '1269213']  # Partidas que você reportou

async def test_finished_detection():
    """Testar se essas partidas aparecem em finished"""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with aiohttp.ClientSession() as session:
        # Teste 1: Buscar últimas 24h com per_page=50 (ANTIGO - pode perder)
        print("\n" + "="*70)
        print("TESTE 1: Busca ANTIGA (24h, per_page=50) - PODE PERDER PARTIDAS")
        print("="*70)
        
        try:
            async with session.get(
                "https://api.pandascore.co/csgo/matches/past",
                headers=headers,
                params={"filter[status]": "finished", "per_page": 50, "sort": "-end_at"}
            ) as resp:
                data = await resp.json()
                finished_ids_old = {m['id'] for m in data}
                
                for match_id in MATCH_IDS:
                    if int(match_id) in finished_ids_old:
                        print(f"✅ {match_id}: ENCONTRADO")
                    else:
                        print(f"❌ {match_id}: NÃO ENCONTRADO")
                
                print(f"\nTotal de partidas retornadas: {len(data)}")
        except Exception as e:
            print(f"Erro: {e}")
        
        # Teste 2: Buscar últimas 24h com per_page=100 (NOVO - melhor)
        print("\n" + "="*70)
        print("TESTE 2: Busca NOVA (24h, per_page=100) - MELHOR COBERTURA")
        print("="*70)
        
        try:
            async with session.get(
                "https://api.pandascore.co/csgo/matches/past",
                headers=headers,
                params={"filter[status]": "finished", "per_page": 100, "sort": "-end_at"}
            ) as resp:
                data = await resp.json()
                finished_ids_new = {m['id'] for m in data}
                
                found_count = 0
                for match_id in MATCH_IDS:
                    if int(match_id) in finished_ids_new:
                        match = next((m for m in data if m['id'] == int(match_id)), None)
                        print(f"✅ {match_id}: ENCONTRADO - Status: {match.get('status')} - Score: {match.get('results', [])}")
                        found_count += 1
                    else:
                        print(f"❌ {match_id}: NÃO ENCONTRADO")
                
                print(f"\nTotal de partidas retornadas: {len(data)}")
                print(f"Partidas encontradas: {found_count}/{len(MATCH_IDS)}")
                
                # Mostrar status detalhado
                print("\n" + "-"*70)
                print("DETALHES DAS PARTIDAS ENCONTRADAS:")
                print("-"*70)
                for match_id in MATCH_IDS:
                    match = next((m for m in data if m['id'] == int(match_id)), None)
                    if match:
                        print(f"\n🎮 Match {match_id}")
                        print(f"   Status: {match.get('status')}")
                        print(f"   Teams: {match.get('name', 'N/A')}")
                        print(f"   Results: {match.get('results', [])}")
                        print(f"   Winner Type: {match.get('winner_type', 'N/A')}")
                        print(f"   End: {match.get('end_at', 'N/A')}")
        
        except Exception as e:
            print(f"Erro: {e}")
        
        # Comparação
        print("\n" + "="*70)
        print("COMPARAÇÃO")
        print("="*70)
        lost_in_old = finished_ids_new - finished_ids_old
        if lost_in_old:
            print(f"⚠️  Partidas perdidas com per_page=50: {lost_in_old}")
        else:
            print(f"✅ Nenhuma partida perdida")

if __name__ == "__main__":
    asyncio.run(test_finished_detection())
