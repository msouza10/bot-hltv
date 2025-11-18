#!/usr/bin/env python3
"""
Script para ver EXATAMENTE o que a API Twitch está retornando como título.
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
    print("TÍTULOS REAIS RETORNADOS PELA API TWITCH")
    print("=" * 100)
    print("\nBuscando por: 'CCT Europe'\n")
    
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    params = {
        "query": "CCT Europe",
        "first": 50,
        "language": "pt"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                
                print(f"Encontradas {len(streams)} streams:\n")
                
                for i, stream in enumerate(streams, 1):
                    channel = stream.get('user_login', 'unknown')
                    title = stream.get('title', 'N/A')
                    viewers = stream.get('viewer_count', 0)
                    
                    # Mostra de forma clara o título exato
                    print(f"{i:2d}. Canal: {channel:20s} | Viewers: {viewers:6,d}")
                    print(f"     TÍTULO EXATO: {title}")
                    
                    # Agora extrai keywords como o algoritmo faz
                    from src.services.twitch_search_service import TwitchSearchService as TSS
                    tsvc = TSS()
                    keywords = tsvc._find_best_match.__code__.co_consts  # Não funciona assim...
                    
                    # Fazer manualmente
                    def extract_keywords(text: str):
                        if not text:
                            return []
                        text = text.lower()
                        words = text.split()
                        keywords = []
                        for word in words:
                            clean_word = word.strip('.,;:!?)[]"\'|🔴')
                            if clean_word:
                                keywords.append(clean_word)
                        return keywords
                    
                    keywords = extract_keywords(title)
                    print(f"     Keywords: {keywords}")
                    
                    # Checar se tem as palavras que procuramos
                    has_betera = "betera" in keywords
                    has_leo = "leo" in keywords
                    has_cct = "cct" in keywords
                    has_europe = "europe" in keywords
                    
                    print(f"     Has: betera={has_betera}, leo={has_leo}, cct={has_cct}, europe={has_europe}\n")
    
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(main())
