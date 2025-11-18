#!/usr/bin/env python3
"""
Script para ver os títulos reais das streams retornadas pela Twitch API.
"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.twitch_search_service import TwitchSearchService

logging.basicConfig(level=logging.WARNING)

async def main():
    """Função principal"""
    service = TwitchSearchService()
    
    print("=" * 80)
    print("Buscando streams com query: 'CCT Europe Betera Esports Leo Team'")
    print("=" * 80)
    
    # Buscar streams
    token = await service._get_access_token()
    if not token:
        print("❌ Erro ao obter token")
        return
    
    streams = await service._search_twitch_api(
        token=token,
        query="CCT Europe Betera Esports Leo Team",
        language="pt",
        championship="CCT Europe",
        team1="Betera Esports",
        team2="Leo Team"
    )
    
    print(f"\n❌ Nenhuma stream encontrada (score baixo)")
    print("\nVou buscar os títulos brutos da API sem filtro:\n")
    
    # Buscar sem filtro de scoring para ver os títulos
    import aiohttp
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    params = {
        "query": "CCT Europe",
        "first": 20,
        "language": "pt"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                
                if streams:
                    print(f"Encontrados {len(streams)} streams:\n")
                    for i, stream in enumerate(streams, 1):
                        print(f"{i}. {stream.get('user_login')}")
                        print(f"   Título: {stream.get('title')}")
                        print(f"   Viewers: {stream.get('viewer_count'):,}\n")
                else:
                    print("Nenhuma stream com 'CCT Europe' encontrada")

if __name__ == "__main__":
    asyncio.run(main())
