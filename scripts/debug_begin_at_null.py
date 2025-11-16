#!/usr/bin/env python3
"""
Script para debugar por que algumas partidas vêm sem begin_at do banco
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.cache_manager import MatchCacheManager

load_dotenv()

async def main():
    db_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    auth_token = os.getenv("LIBSQL_AUTH_TOKEN")
    
    cache_manager = MatchCacheManager(db_url, auth_token)
    client = await cache_manager.get_client()
    
    print("\n" + "=" * 80)
    print("🔍 DEBUG - Partidas com begin_at = NULL no banco")
    print("=" * 80 + "\n")
    
    # Buscar partidas com begin_at NULL
    result = await client.execute(
        """
        SELECT match_id, status, tournament_name, begin_at, 
               SUBSTR(match_data, 1, 200) as match_data_preview
        FROM matches_cache
        WHERE begin_at IS NULL
        LIMIT 10
        """,
        []
    )
    
    rows = result.rows if result.rows else []
    
    print(f"📊 Total de partidas com begin_at = NULL: {len(rows)}\n")
    
    if not rows:
        print("✅ Nenhuma partida com begin_at nulo!")
    else:
        for idx, row in enumerate(rows, 1):
            match_id = row[0]
            status = row[1]
            tournament = row[2]
            begin_at = row[3]
            preview = row[4]
            
            print(f"Partida #{idx}:")
            print(f"  ID: {match_id}")
            print(f"  Status: {status}")
            print(f"  Torneio: {tournament}")
            print(f"  begin_at: {begin_at}")
            print(f"  Preview: {preview}")
            print()
            
            # Buscar dados completos
            result = await client.execute(
                "SELECT match_data FROM matches_cache WHERE match_id = ?",
                [match_id]
            )
            
            if result.rows:
                match_data_str = result.rows[0][0]
                try:
                    match_data = json.loads(match_data_str)
                    print(f"  ✓ Chaves do JSON: {list(match_data.keys())}")
                    print(f"  ✓ begin_at no JSON: {match_data.get('begin_at')}")
                    print(f"  ✓ scheduled_at no JSON: {match_data.get('scheduled_at')}")
                    print(f"  ✓ status no JSON: {match_data.get('status')}")
                except:
                    print(f"  ❌ Erro ao parsear JSON")
            print()
    
    # Agora vamos ver TODAS as partidas e qual é o pattern
    print("\n[2️⃣ PARTIDAS COM begin_at VÁLIDO]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT status)
        FROM matches_cache
        WHERE begin_at IS NOT NULL
        """,
        []
    )
    
    if result.rows:
        total_com_begin = result.rows[0][0]
        print(f"✅ Total de partidas COM begin_at: {total_com_begin}\n")
    
    # Verificar padrão
    result = await client.execute(
        """
        SELECT status, COUNT(*) as total,
               SUM(CASE WHEN begin_at IS NULL THEN 1 ELSE 0 END) as sem_begin_at
        FROM matches_cache
        GROUP BY status
        """,
        []
    )
    
    if result.rows:
        print("📊 Distribuição por status:")
        for row in result.rows:
            status = row[0]
            total = row[1]
            sem = row[2]
            with_begin = total - sem
            print(f"  {status}: {total} total | {with_begin} com begin_at | {sem} SEM begin_at")

if __name__ == "__main__":
    asyncio.run(main())
