#!/usr/bin/env python3
"""
Script para debugar a estrutura de dados da API PandaScore
Mostra exatamente o que a API está retornando
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.pandascore_service import PandaScoreClient

load_dotenv()

async def main():
    api_key = os.getenv("PANDASCORE_API_KEY")
    if not api_key:
        print("❌ PANDASCORE_API_KEY não configurada!")
        return
    
    client = PandaScoreClient(api_key)
    
    print("\n" + "=" * 80)
    print("🔍 DEBUG - Estrutura de Dados da API PandaScore")
    print("=" * 80 + "\n")
    
    # Buscar partidas próximas
    print("[1️⃣ PARTIDAS PRÓXIMAS]")
    print("-" * 80)
    
    upcoming = await client.get_upcoming_matches(per_page=5)
    
    if not upcoming:
        print("❌ Nenhuma partida próxima retornada")
    else:
        print(f"✅ {len(upcoming)} partidas retornadas\n")
        
        for idx, match in enumerate(upcoming[:2], 1):  # Mostrar apenas as 2 primeiras
            print(f"Partida #{idx}:")
            print(f"  ID: {match.get('id')}")
            print(f"  Status: {match.get('status')}")
            print(f"  begin_at: {match.get('begin_at')}")
            print(f"  scheduled_at: {match.get('scheduled_at')}")
            print(f"  Chaves disponíveis: {list(match.keys())}")
            print()
    
    # Mostrar JSON completo da primeira partida
    if upcoming:
        print("\n[2️⃣ JSON COMPLETO - PRIMEIRA PARTIDA]")
        print("-" * 80)
        print(json.dumps(upcoming[0], indent=2, default=str))
    
    await client.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
