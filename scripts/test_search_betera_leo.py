#!/usr/bin/env python3
"""
Script para encontrar a stream "Betera vs Leo" que você viu na Twitch.
Vamos testar se a API realmente retorna isso.
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
    print("PROCURANDO: Streams com 'BETERA' ou 'LEO' no título")
    print("=" * 100)
    
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    params = {
        "game_id": "32399",  # Counter-Strike
        "first": 100,
        "language": "pt"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                
                print(f"\nTotal de streams retornadas: {len(streams)}\n")
                
                # Procurar por "betera" ou "leo"
                found = []
                for stream in streams:
                    title = stream.get('title', '').lower()
                    login = stream.get('user_login', '').lower()
                    
                    if 'betera' in title or 'betera' in login or 'leo' in title or 'leo' in login:
                        found.append(stream)
                
                if found:
                    print(f"✅ ENCONTROU {len(found)} stream(s) com BETERA ou LEO:\n")
                    for stream in found:
                        print(f"  Canal: {stream['user_login']}")
                        print(f"  Título: {stream['title']}")
                        print(f"  Viewers: {stream['viewer_count']:,}")
                        print(f"  Game: {stream['game_name']}")
                        print()
                else:
                    print("❌ NENHUMA stream encontrada com 'betera' ou 'leo'\n")
                    print("Primeiras 10 streams retornadas:")
                    for i, stream in enumerate(streams[:10], 1):
                        print(f"{i}. {stream['user_login']:20s} | {stream['title'][:60]}")

if __name__ == "__main__":
    asyncio.run(main())
