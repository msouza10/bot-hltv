#!/usr/bin/env python3
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

from src.services.pandascore_service import PandaScoreClient

async def analyze_match_data():
    client = PandaScoreClient(os.getenv("PANDASCORE_API_KEY"))
    
    print("=" * 80)
    print("ANALISANDO ESTRUTURA DE DADOS POR STATUS")
    print("=" * 80)
    
    # 1. NOT_STARTED
    print("\n1️⃣  NOT_STARTED (Futuro)")
    print("-" * 80)
    upcoming = await client.get_upcoming_matches(per_page=1)
    if upcoming:
        m = upcoming[0]
        print(f"ID: {m['id']}")
        print(f"Status: {m['status']}")
        print(f"begin_at: {m.get('begin_at')}")
        print(f"end_at: {m.get('end_at')}")
        print(f"scheduled_at: {m.get('scheduled_at')}")
        print(f"results: {m.get('results')}")
        print(f"games: {len(m.get('games', []))} mapas")
        print(f"Tem scores? {any(r.get('score', 0) > 0 for r in m.get('results', []))}")
    
    # 2. RUNNING
    print("\n2️⃣  RUNNING (Ao Vivo)")
    print("-" * 80)
    running = await client.get_running_matches()
    if running:
        m = running[0]
        print(f"ID: {m['id']}")
        print(f"Status: {m['status']}")
        print(f"begin_at: {m.get('begin_at')}")
        print(f"end_at: {m.get('end_at')}")
        print(f"scheduled_at: {m.get('scheduled_at')}")
        print(f"results: {m.get('results')}")
        print(f"games: {len(m.get('games', []))} mapas")
        print(f"Tem scores? {any(r.get('score', 0) > 0 for r in m.get('results', []))}")
        if m.get('games'):
            print(f"Games com scores: {sum(1 for g in m.get('games', []) if g.get('results'))}")
    
    # 3. FINISHED
    print("\n3️⃣  FINISHED (Finalizado)")
    print("-" * 80)
    finished = await client.get_past_matches(per_page=1)
    if finished:
        m = finished[0]
        print(f"ID: {m['id']}")
        print(f"Status: {m['status']}")
        print(f"begin_at: {m.get('begin_at')}")
        print(f"end_at: {m.get('end_at')}")
        print(f"scheduled_at: {m.get('scheduled_at')}")
        print(f"results: {m.get('results')}")
        print(f"games: {len(m.get('games', []))} mapas")
        print(f"Tem scores? {any(r.get('score', 0) > 0 for r in m.get('results', []))}")
        if m.get('games'):
            print(f"Games com scores: {sum(1 for g in m.get('games', []) if g.get('results'))}")
            print(f"\nPrimeiro mapa:")
            g = m['games'][0]
            print(f"  Name: {g.get('name')}")
            print(f"  Map: {g.get('map', {}).get('name')}")
            print(f"  Results: {g.get('results')}")
    
    # 4. CANCELED
    print("\n4️⃣  CANCELED (Cancelado)")
    print("-" * 80)
    canceled = await client.get_canceled_matches(per_page=1)
    if canceled:
        m = canceled[0]
        print(f"ID: {m['id']}")
        print(f"Status: {m['status']}")
        print(f"begin_at: {m.get('begin_at')}")
        print(f"end_at: {m.get('end_at')}")
        print(f"scheduled_at: {m.get('scheduled_at')}")
        print(f"results: {m.get('results')}")
        print(f"games: {len(m.get('games', []))} mapas")
        print(f"Tem scores? {any(r.get('score', 0) > 0 for r in m.get('results', []))}")
    
    print("\n" + "=" * 80)
    print("COMPARAÇÃO DE CAMPOS DISPONÍVEIS")
    print("=" * 80)
    
    print("\n✅ Como identificar cada status:\n")
    print("NOT_STARTED:")
    print("  - status = 'not_started'")
    print("  - begin_at: data futura")
    print("  - results: [0, 0] ou vazio")
    print("  - games: lista de mapas, mas sem resultados")
    print("  → Usar: begin_at no futuro + status='not_started'\n")
    
    print("RUNNING:")
    print("  - status = 'running'")
    print("  - begin_at: passou")
    print("  - end_at: NULL (ainda jogando)")
    print("  - results: pode ter scores parciais")
    print("  - games: mapas em progresso ou completos")
    print("  → Usar: status='running'\n")
    
    print("FINISHED:")
    print("  - status = 'finished'")
    print("  - begin_at: passou")
    print("  - end_at: pode ser NULL (API não preenche para CS2)")
    print("  - results: [score_team1, score_team2] com scores finais")
    print("  - games: todos os mapas com resultados completos")
    print("  → Usar: status='finished' + results com scores > 0\n")
    
    print("CANCELED:")
    print("  - status = 'canceled'")
    print("  - begin_at: NULL (foi cancelado antes de começar)")
    print("  - end_at: NULL")
    print("  - results: [0, 0]")
    print("  - games: lista de mapas planejados, sem resultados")
    print("  → Usar: status='canceled'\n")
    
    await client.close()

asyncio.run(analyze_match_data())
