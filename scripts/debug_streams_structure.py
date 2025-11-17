#!/usr/bin/env python3
"""
Debug script: Ver exatamente como a API retorna streams
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")

from src.services.pandascore_service import PandaScoreClient


async def debug_streams():
    """Inspeciona estrutura real de streams da API"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: Estrutura real de streams da API")
    print("="*80 + "\n")
    
    api = PandaScoreClient(PANDASCORE_API_KEY)
    
    # Buscar running matches
    print("1️⃣  Buscando running matches da API...")
    matches = await api.get_running_matches()
    
    if not matches:
        print("   ℹ️  Nenhum match ao vivo no momento\n")
        return
    
    print(f"   ✅ {len(matches)} matches encontrados\n")
    
    # Verificar o primeiro com streams_list
    for i, match in enumerate(matches):
        if match.get("streams_list"):
            print(f"2️⃣  Match {i}: {match.get('name')}")
            print(f"   Streams count: {len(match['streams_list'])}\n")
            
            # Mostrar estrutura de cada stream
            for j, stream in enumerate(match["streams_list"]):
                print(f"   Stream {j}:")
                print(f"      Campos disponíveis: {list(stream.keys())}")
                print(f"      Raw JSON:\n")
                
                # Pretty print
                json_str = json.dumps(stream, indent=6)
                for line in json_str.split("\n"):
                    print(f"         {line}")
                
                print()
            
            # Análise
            print("   📊 ANÁLISE:")
            print(f"      - Tem 'raw_url'? {any('raw_url' in s for s in match['streams_list'])}")
            print(f"      - Tem 'url'? {any('url' in s for s in match['streams_list'])}")
            print(f"      - Tem 'embed_url'? {any('embed_url' in s for s in match['streams_list'])}")
            print(f"      - Tem 'link'? {any('link' in s for s in match['streams_list'])}")
            print()
            
            break


async def main():
    try:
        await debug_streams()
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
