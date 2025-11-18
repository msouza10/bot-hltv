#!/usr/bin/env python3
"""
Script para buscar canais específicos na Twitch (alternativa à busca de streams genérica).
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
    
    # Tentar nomes de canais
    channel_names = [
        "betera",
        "betera_esports",
        "beterapro",
        "leo",
        "leoteam",
        "leo_team",
        "ccteurope",
        "cct_europe",
        "pandascore"
    ]
    
    print("=" * 100)
    print("BUSCANDO CANAIS DIRETOS NA TWITCH")
    print("=" * 100)
    
    for channel_name in channel_names:
        print(f"\n🔍 Procurando canal: {channel_name}")
        
        url = "https://api.twitch.tv/helix/channels"
        headers = {
            "Client-ID": service.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "broadcaster_login": channel_name
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    channels = data.get("data", [])
                    
                    if channels:
                        for ch in channels:
                            print(f"   ✅ Encontrado!")
                            print(f"      Nome: {ch.get('broadcaster_name')}")
                            print(f"      Login: {ch.get('broadcaster_login')}")
                            print(f"      Game: {ch.get('game_name')}")
                            print(f"      Status: {ch.get('title')}")
                    else:
                        print(f"   ❌ Não encontrado")

if __name__ == "__main__":
    asyncio.run(main())
