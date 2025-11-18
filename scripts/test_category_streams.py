#!/usr/bin/env python3
"""
Script para buscar streams da CATEGORIA "Counter-Strike 2" ao invés de buscar por query.
Isso é mais confiável que buscar por string.
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
    print("BUSCANDO STREAMS DA CATEGORIA 'Counter-Strike 2'")
    print("=" * 100)
    
    # Primeiro, pegar o ID da categoria
    print("\n1️⃣ Procurando ID da categoria 'Counter-Strike 2'...\n")
    
    url = "https://api.twitch.tv/helix/search/categories"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    params = {
        "query": "Counter-Strike 2",
        "first": 10
    }
    
    category_id = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                categories = data.get("data", [])
                
                for cat in categories:
                    print(f"   ID: {cat['id']}, Nome: {cat['name']}")
                    # Procurar por "Counter-Strike" genérico (ID 32399)
                    if cat['id'] == 32399:  # Counter-Strike
                        category_id = cat['id']
                        print(f"   ✅ Usando categoria genérica 'Counter-Strike'! ID: {category_id}\n")
                        break
    
    if not category_id:
        category_id = 32399  # Hardcode como fallback
        print(f"   ⚠️ Usando ID hardcoded: {category_id}\n")
    
    # Agora buscar streams NESSA categoria
    print("2️⃣ Buscando streams na categoria Counter-Strike 2...\n")
    
    url = "https://api.twitch.tv/helix/streams"
    params = {
        "game_id": category_id,
        "first": 50,
        "language": "pt"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                
                print(f"Encontradas {len(streams)} streams de Counter-Strike 2:\n")
                
                for i, stream in enumerate(streams[:15], 1):
                    channel = stream.get('user_login', 'unknown')
                    title = stream.get('title', 'N/A')
                    viewers = stream.get('viewer_count', 0)
                    
                    print(f"{i:2d}. {channel:25s} | {viewers:6,d} viewers")
                    print(f"     {title[:80]}")
                    
                    # Procurar por "betera" ou "leo"
                    if "betera" in title.lower() or "leo" in title.lower():
                        print(f"     ✅ ENCONTROU 'betera' ou 'leo'!")
                    print()

if __name__ == "__main__":
    asyncio.run(main())
