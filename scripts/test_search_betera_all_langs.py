#!/usr/bin/env python3
"""
Script para procurar 'Betera vs Leo' SEM filtro de language.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import aiohttp

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.twitch_search_service import TwitchSearchService

async def main():
    """Função principal"""
    service = TwitchSearchService()
    
    token = await service._get_access_token()
    if not token:
        print("❌ Erro ao obter token")
        return
    
    print("=" * 100)
    print("PROCURANDO: Streams 'Betera' ou 'Leo' SEM filtro de linguagem")
    print("=" * 100)
    
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    
    # Teste 1: Sem language filter
    print("\n[TESTE 1] game_id=32399, first=100 (SEM language filter)")
    params = {
        "game_id": "32399",  # Counter-Strike
        "first": 100,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                print(f"Total: {len(streams)} streams")
                
                # Procurar por "betera" ou "leo"
                found = []
                for stream in streams:
                    title = stream.get('title', '').lower()
                    login = stream.get('user_login', '').lower()
                    
                    if ('betera' in title and 'leo' in title) or \
                       ('betera' in login and 'leo' in login):
                        found.append(stream)
                
                if found:
                    print(f"✅ ENCONTROU {len(found)} stream(s) com BETERA E LEO juntos:\n")
                    for stream in found:
                        print(f"  Canal: {stream['user_login']}")
                        print(f"  Título: {stream['title']}")
                        print(f"  Viewers: {stream['viewer_count']:,}")
                        print(f"  Idioma: {stream.get('language', 'N/A')}")
                        print()
                else:
                    print("❌ Nenhuma stream encontrada com BETERA E LEO juntos\n")
                    
                    # Mostrar streams que contêm apenas uma dessas palavras
                    betera_only = [s for s in streams if 'betera' in s.get('title', '').lower()]
                    leo_only = [s for s in streams if 'leo' in s.get('title', '').lower()]
                    
                    if betera_only or leo_only:
                        print(f"Mas encontrou {len(betera_only)} com 'betera' e {len(leo_only)} com 'leo'\n")
                        
                        print("Streams com 'betera' no título:")
                        for s in betera_only[:5]:
                            print(f"  - {s['user_login']:20s} | {s['title'][:70]}")
                        
                        print("\nStreams com 'leo' no título:")
                        for s in leo_only[:5]:
                            print(f"  - {s['user_login']:20s} | {s['title'][:70]}")
                    else:
                        print("Nenhuma stream com 'betera' ou 'leo' encontrada")
                        print("\nPrimeiras 15 streams disponíveis:")
                        for i, stream in enumerate(streams[:15], 1):
                            print(f"{i:2d}. {stream['user_login']:20s} | {stream['title'][:60]}")

if __name__ == "__main__":
    asyncio.run(main())
