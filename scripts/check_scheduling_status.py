#!/usr/bin/env python3
"""
Script para verificar se lembretes foram agendados para as próximas partidas
"""

import asyncio
import json
import os
import sys
from datetime import datetime
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
    print("🔍 STATUS DE AGENDAMENTO DE LEMBRETES")
    print("=" * 80 + "\n")
    
    # 1. Verificar partidas próximas
    print("[1️⃣ PRÓXIMAS PARTIDAS (not_started)]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT match_id, status, begin_at
        FROM matches_cache
        WHERE status = 'not_started'
        ORDER BY begin_at ASC
        LIMIT 5
        """,
        []
    )
    
    upcoming = result.rows if result.rows else []
    print(f"Total próximas: {len(upcoming)}\n")
    
    for match in upcoming:
        match_id = match[0]
        status = match[1]
        begin_at = match[2]
        
        print(f"Partida ID: {match_id}")
        print(f"  Status: {status}")
        print(f"  Begin_at: {begin_at}")
        print()
    
    # 2. Verificar lembretes agendados
    print("\n[2️⃣ LEMBRETES AGENDADOS]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT COUNT(*) FROM match_reminders WHERE sent = 0
        """,
        []
    )
    
    pending_count = result.rows[0][0] if result.rows else 0
    print(f"Total de lembretes pendentes: {pending_count}\n")
    
    if pending_count == 0:
        print("❌ NENHUM LEMBRETE AGENDADO!")
    else:
        # Mostrar distribuição
        result = await client.execute(
            """
            SELECT reminder_minutes_before, COUNT(*) as count
            FROM match_reminders
            WHERE sent = 0
            GROUP BY reminder_minutes_before
            ORDER BY reminder_minutes_before DESC
            """,
            []
        )
        
        print("Lembretes por tipo:")
        for row in result.rows:
            minutes = row[0]
            count = row[1]
            print(f"  • {minutes} minutos antes: {count} lembretes")
    
    # 3. Verificar se há lembretes para as partidas próximas
    print("\n[3️⃣ LEMBRETES PARA PRÓXIMAS PARTIDAS]")
    print("-" * 80)
    
    for match in upcoming[:3]:  # Check first 3
        match_id = match[0]
        
        result = await client.execute(
            """
            SELECT COUNT(*) FROM match_reminders 
            WHERE match_id = ? AND sent = 0
            """,
            [match_id]
        )
        
        count = result.rows[0][0] if result.rows else 0
        
        if count > 0:
            print(f"✅ Partida {match_id}: {count} lembretes agendados")
        else:
            print(f"❌ Partida {match_id}: NENHUM lembrete agendado!")
    
    # 4. Verificar configuração de notificações
    print("\n[4️⃣ CONFIGURAÇÃO DE NOTIFICAÇÕES]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT guild_id, notify_upcoming, notify_live, notification_channel_id
        FROM guild_config
        """,
        []
    )
    
    if not result.rows:
        print("❌ Nenhuma guild configurada!")
    else:
        for row in result.rows:
            guild_id = row[0]
            notify_upcoming = row[1]
            notify_live = row[2]
            channel_id = row[3]
            
            print(f"Guild: {guild_id}")
            print(f"  Notificações ativas: {notify_upcoming == 1}")
            print(f"  Canal: {channel_id}")
            print()
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
