#!/usr/bin/env python3
"""
Script para verificar streams do YouTube no banco de dados e na API.
"""

import asyncio
import json
import sqlite3
import os
from dotenv import load_dotenv
from src.services.pandascore_service import PandaScoreClient

load_dotenv()

async def check_api():
    """Verifica o que vem da API PandaScore para YouTube"""
    print("\n" + "="*80)
    print("📡 VERIFICANDO API PANDASCORE")
    print("="*80)
    
    client = PandaScoreClient()
    try:
        matches = await client.get_running_matches()
        if matches:
            for match in matches[:5]:
                match_id = match.get("id")
                streams = match.get("streams_list", [])
                
                youtube_streams = [s for s in streams if "youtube" in s.get("raw_url", "").lower()]
                
                if youtube_streams:
                    print(f"\n✅ Match {match_id}:")
                    print(f"   Streams YouTube encontradas: {len(youtube_streams)}")
                    for i, stream in enumerate(youtube_streams):
                        print(f"\n   Stream #{i+1}:")
                        print(f"     raw_url: {stream.get('raw_url', 'N/A')}")
                        print(f"     title: {stream.get('title', 'N/A')}")
                        print(f"     official: {stream.get('official', False)}")
                        print(f"     language: {stream.get('language', 'unknown')}")
                        print(f"   Todas as chaves: {list(stream.keys())}")
    finally:
        await client.close()


def check_database():
    """Verifica o que está armazenado no banco de dados"""
    print("\n" + "="*80)
    print("💾 VERIFICANDO BANCO DE DADOS")
    print("="*80)
    
    conn = sqlite3.connect("data/bot.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Buscar todos os streams do YouTube
        cursor.execute("""
            SELECT match_id, platform, channel_name, url, raw_url, language, title, is_official
            FROM match_streams
            WHERE platform = 'youtube'
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n✅ Encontrados {len(rows)} streams do YouTube no banco:")
            for row in rows:
                print(f"\n   Match ID: {row['match_id']}")
                print(f"   Platform: {row['platform']}")
                print(f"   Channel Name: {row['channel_name']}")
                print(f"   Raw URL: {row['raw_url']}")
                print(f"   Title (IMPORTANTE): '{row['title']}'")
                print(f"   Language: {row['language']}")
                print(f"   Is Official: {row['is_official']}")
        else:
            print("\n❌ Nenhum stream do YouTube encontrado no banco de dados")
            
    finally:
        conn.close()


if __name__ == "__main__":
    print("🔍 Checando YouTube Streams...")
    
    # Verificar banco primeiro
    check_database()
    
    # Depois verificar API
    if os.getenv("PANDASCORE_API_KEY"):
        asyncio.run(check_api())
    else:
        print("\n⚠️ PANDASCORE_API_KEY não configurada, pulando verificação de API")
