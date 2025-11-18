#!/usr/bin/env python3
"""
Debug detalhado: Ver exatamente qual stream está sendo selecionada e por quê.
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
    
    print("=" * 100)
    print("DEBUG: Todas as streams retornadas pela API")
    print("=" * 100)
    print()
    
    token = await service._get_access_token()
    if not token:
        print("❌ Erro ao obter token")
        return
    
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": service.client_id,
        "Authorization": f"Bearer {token}"
    }
    
    # Buscar com game_id=32399 (Counter-Strike) SEM language filter
    params = {
        "game_id": "32399",
        "first": 100,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                streams = data.get("data", [])
                
                print(f"Total: {len(streams)} streams\n")
                
                # Procurar por "betera" ou "leo"
                print("Streams que contêm 'Betera' ou 'Leo':")
                print("=" * 100)
                
                for stream in streams:
                    title = stream.get('title', '')
                    title_lower = title.lower()
                    
                    if 'betera' in title_lower or 'leo' in title_lower:
                        print(f"Canal: {stream['user_login']}")
                        print(f"Título: {title}")
                        print(f"Viewers: {stream['viewer_count']:,}")
                        print(f"Idioma: {stream.get('language', 'N/A')}")
                        
                        # Calcular score
                        championship = "CCT Europe"
                        team1 = "Betera"
                        team2 = "Leo"
                        
                        # Score por campeonato
                        score = 0
                        if "cct" in title_lower:
                            score += 10
                            print(f"  ✓ Encontrou 'cct' +10")
                        if "europe" in title_lower:
                            score += 10
                            print(f"  ✓ Encontrou 'europe' +10")
                        if "betera" in title_lower:
                            score += 20
                            print(f"  ✓ Encontrou 'betera' (time) +20")
                        if "leo" in title_lower:
                            score += 20
                            print(f"  ✓ Encontrou 'leo' (time) +20")
                        
                        # Language bonus
                        if stream.get('language') == 'pt':
                            score += 50
                            print(f"  ✓ Idioma PT +50")
                        elif stream.get('language') == 'ru':
                            score += 10
                            print(f"  ✓ Idioma RU +10")
                        
                        print(f"  SCORE TOTAL: {score}\n")
                
                # Agora encontrar a stream de MAIOR score
                print("\n" + "=" * 100)
                print("RESUMO POR SCORE:")
                print("=" * 100 + "\n")
                
                scores = []
                for stream in streams:
                    title = stream.get('title', '')
                    title_lower = title.lower()
                    
                    if 'betera' in title_lower or 'leo' in title_lower:
                        championship = "CCT Europe"
                        team1 = "Betera"
                        team2 = "Leo"
                        
                        score = 0
                        if "cct" in title_lower:
                            score += 10
                        if "europe" in title_lower:
                            score += 10
                        if "betera" in title_lower:
                            score += 20
                        if "leo" in title_lower:
                            score += 20
                        if stream.get('language') == 'pt':
                            score += 50
                        elif stream.get('language') == 'ru':
                            score += 10
                        
                        scores.append((score, stream))
                
                # Ordenar por score DESC
                scores.sort(key=lambda x: x[0], reverse=True)
                
                print("Top 5 streams por score:")
                for i, (score, stream) in enumerate(scores[:5], 1):
                    print(f"{i}. [{score:3d} pts] {stream['user_login']:20s} | {stream['title'][:60]}")

if __name__ == "__main__":
    asyncio.run(main())
