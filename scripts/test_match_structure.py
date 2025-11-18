#!/usr/bin/env python3
"""
Script para verificar a estrutura dos matches retornados pelo PandaScore
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.pandascore_service import PandaScoreClient

async def main():
    """Função principal"""
    
    print("=" * 100)
    print("DEBUG: Estrutura dos Matches Retornados pelo PandaScore")
    print("=" * 100)
    print()
    
    client = PandaScoreClient()
    
    try:
        matches = await client.get_running_matches()
        
        print(f"Total de matches: {len(matches)}\n")
        
        if matches:
            match = matches[0]
            
            print("Primeiro match - ESTRUTURA COMPLETA:")
            print(json.dumps(match, indent=2, ensure_ascii=False, default=str)[:2000])
            
            print("\n" + "=" * 100)
            print("EXTRAÇÃO DE DADOS DO PRIMEIRO MATCH:")
            print("=" * 100)
            print(f"Match ID: {match.get('id')}")
            print(f"Status: {match.get('status')}")
            print(f"Tournament: {match.get('tournament')}")
            print(f"Opponents: {match.get('opponents')}")
            
            if match.get('opponents'):
                print(f"\nTotal de opponents: {len(match.get('opponents'))}")
                for i, opp in enumerate(match.get('opponents'), 1):
                    print(f"  Opponent {i}:")
                    print(f"    ID: {opp.get('id')}")
                    print(f"    Name: {opp.get('name')}")
                    print(f"    Team: {opp.get('team')}")
                    if opp.get('team'):
                        print(f"      Team ID: {opp['team'].get('id')}")
                        print(f"      Team Name: {opp['team'].get('name')}")
    
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
