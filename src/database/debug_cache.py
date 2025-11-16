#!/usr/bin/env python3
"""
Script para debug do cache - mostra o estado real das partidas
"""

import asyncio
import os
from dotenv import load_dotenv
import libsql_client

load_dotenv()

DB_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")


async def main():
    if AUTH_TOKEN:
        client = libsql_client.create_client(url=DB_URL, auth_token=AUTH_TOKEN)
    else:
        client = libsql_client.create_client(url=DB_URL)
    
    print("\n📊 DEBUG - Estado do Cache")
    print("=" * 60)
    
    # Mostrar estatísticas da view
    print("\n1️⃣ Estatísticas (VIEW cache_stats):")
    result = await client.execute("SELECT * FROM cache_stats")
    if result.rows:
        row = result.rows[0]
        print(f"   Total de partidas: {row['total_matches']}")
        print(f"   Próximas (not_started): {row['upcoming_matches']}")
        print(f"   Ao vivo (running): {row['live_matches']}")
        print(f"   Finalizadas (finished): {row['finished_matches']}")
        print(f"   Atualizadas nos últimos 15min: {row['recently_updated']}")
        print(f"   Atualização mais antiga: {row['oldest_update']}")
        print(f"   Atualização mais recente: {row['newest_update']}")
    
    # Mostrar partidas ao vivo
    print("\n2️⃣ Partidas AO VIVO (status='running'):")
    result = await client.execute("""
        SELECT match_id, status, tournament_name, begin_at, end_at, updated_at 
        FROM matches_cache 
        WHERE status = 'running'
        ORDER BY updated_at DESC
    """)
    
    if result.rows:
        print(f"   Encontradas {len(result.rows)} partidas ao vivo:")
        for i, row in enumerate(result.rows, 1):
            print(f"\n   {i}. ID: {row['match_id']}")
            print(f"      Status: {row['status']}")
            print(f"      Torneio: {row['tournament_name']}")
            print(f"      Começo: {row['begin_at']}")
            print(f"      Fim: {row['end_at']}")
            print(f"      Atualizado: {row['updated_at']}")
    else:
        print("   ❌ Nenhuma partida ao vivo encontrada!")
    
    # Mostrar últimas 5 partidas inseridas
    print("\n3️⃣ Últimas 5 partidas cacheadas:")
    result = await client.execute("""
        SELECT match_id, status, tournament_name, begin_at, end_at, updated_at 
        FROM matches_cache 
        ORDER BY updated_at DESC
        LIMIT 5
    """)
    
    for i, row in enumerate(result.rows, 1):
        print(f"\n   {i}. ID: {row['match_id']} | Status: {row['status']}")
        print(f"      Torneio: {row['tournament_name']}")
        print(f"      Atualizado: {row['updated_at']}")
    
    # Mostrar histórico de atualizações
    print("\n4️⃣ Histórico de atualizações do cache:")
    result = await client.execute("""
        SELECT update_type, matches_updated, matches_added, status, completed_at
        FROM cache_update_log
        ORDER BY completed_at DESC
        LIMIT 5
    """)
    
    for i, row in enumerate(result.rows, 1):
        print(f"\n   {i}. Tipo: {row['update_type']}")
        print(f"      Atualizadas: {row['matches_updated']} | Adicionadas: {row['matches_added']}")
        print(f"      Status: {row['status']}")
        print(f"      Quando: {row['completed_at']}")
    
    print("\n" + "=" * 60 + "\n")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
