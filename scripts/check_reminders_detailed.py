#!/usr/bin/env python3
"""
Script para verificar status detalhado dos lembretes agendados.
Mostra quanto tempo falta para cada lembrete ser enviado.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Adicionar src ao path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.cache_manager import MatchCacheManager

load_dotenv()

LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

async def main():
    print("\n" + "=" * 80)
    print("📊 ANÁLISE DETALHADA DE LEMBRETES")
    print("=" * 80)
    
    cache_manager = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    client = await cache_manager.get_client()
    
    now = datetime.now()
    print(f"\n⏰ Hora atual: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Verificar todos os lembretes pendentes
    print("\n[1️⃣ LEMBRETES PENDENTES]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT 
            mr.id,
            mr.guild_id,
            mr.match_id,
            mr.reminder_minutes_before,
            mr.scheduled_time,
            mr.sent,
            mc.match_data
        FROM match_reminders mr
        LEFT JOIN matches_cache mc ON mr.match_id = mc.match_id
        WHERE mr.sent = 0
        ORDER BY mr.scheduled_time ASC
        """,
        []
    )
    
    pending_reminders = result.rows if result.rows else []
    
    if not pending_reminders:
        print("✅ Nenhum lembrete pendente!")
    else:
        print(f"⏳ Total de lembretes pendentes: {len(pending_reminders)}\n")
        
        for idx, reminder in enumerate(pending_reminders, 1):
            reminder_id = reminder[0]
            guild_id = reminder[1]
            match_id = reminder[2]
            minutes_before = reminder[3]
            scheduled_time_str = reminder[4]
            sent = reminder[5]
            match_data = reminder[6]
            
            scheduled_time = datetime.fromisoformat(scheduled_time_str)
            time_until = scheduled_time - now
            
            # Determinar status
            if time_until.total_seconds() <= 0:
                status = "🚀 PRONTO PARA ENVIAR"
                time_display = "JÁ VENCIDO"
            else:
                seconds = int(time_until.total_seconds())
                minutes = seconds // 60
                secs = seconds % 60
                time_display = f"{minutes}m {secs}s"
                status = "⏳ Aguardando"
            
            # Tentar parsear match_data
            try:
                if match_data:
                    match = json.loads(match_data)
                    team1 = match.get('opponents', [{}])[0]
                    team2 = match.get('opponents', [{}])[1] if len(match.get('opponents', [])) > 1 else {}
                    team1_name = team1.get('opponent', {}).get('name', '?') if team1.get('opponent') else '?'
                    team2_name = team2.get('opponent', {}).get('name', '?') if team2.get('opponent') else '?'
                    teams_str = f"{team1_name} vs {team2_name}"
                else:
                    teams_str = "Dados indisponíveis"
            except:
                teams_str = "Erro ao parsear dados"
            
            print(f"  #{idx:2d} | {status}")
            print(f"       • Partida: {match_id} ({teams_str})")
            print(f"       • Tipo: {minutes_before} minutos antes")
            print(f"       • Agendado para: {scheduled_time.strftime('%H:%M:%S')}")
            print(f"       • Falta: {time_display}")
            print(f"       • Guild: {guild_id} | ID Lembrete: {reminder_id}")
            print()
    
    # 2. Verificar lembretes já enviados
    print("\n[2️⃣ LEMBRETES JÁ ENVIADOS]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT 
            mr.id,
            mr.match_id,
            mr.reminder_minutes_before,
            mr.scheduled_time,
            mr.sent_at,
            mc.match_data
        FROM match_reminders mr
        LEFT JOIN matches_cache mc ON mr.match_id = mc.match_id
        WHERE mr.sent = 1
        ORDER BY mr.sent_at DESC
        LIMIT 20
        """,
        []
    )
    
    sent_reminders = result.rows if result.rows else []
    
    if not sent_reminders:
        print("✅ Nenhum lembrete enviado ainda")
    else:
        print(f"📬 Últimos {len(sent_reminders)} lembretes enviados:\n")
        
        for idx, reminder in enumerate(sent_reminders, 1):
            reminder_id = reminder[0]
            match_id = reminder[1]
            minutes_before = reminder[2]
            scheduled_time_str = reminder[3]
            sent_at_str = reminder[4]
            match_data = reminder[5]
            
            scheduled_time = datetime.fromisoformat(scheduled_time_str)
            sent_at = datetime.fromisoformat(sent_at_str) if sent_at_str else None
            
            delay = ""
            if sent_at:
                delay_seconds = (sent_at - scheduled_time).total_seconds()
                if delay_seconds > 0:
                    delay = f" (+{int(delay_seconds)}s)"
            
            try:
                if match_data:
                    match = json.loads(match_data)
                    team1 = match.get('opponents', [{}])[0]
                    team2 = match.get('opponents', [{}])[1] if len(match.get('opponents', [])) > 1 else {}
                    team1_name = team1.get('opponent', {}).get('name', '?') if team1.get('opponent') else '?'
                    team2_name = team2.get('opponent', {}).get('name', '?') if team2.get('opponent') else '?'
                    teams_str = f"{team1_name} vs {team2_name}"
                else:
                    teams_str = "Dados indisponíveis"
            except:
                teams_str = "Erro ao parsear dados"
            
            print(f"  #{idx:2d} | ✅ ENVIADO")
            print(f"       • Partida: {match_id} ({teams_str})")
            print(f"       • Tipo: {minutes_before} minutos antes")
            print(f"       • Enviado em: {sent_at.strftime('%H:%M:%S') if sent_at else 'N/A'}{delay}")
            print()
    
    # 3. Resumo por tipo de lembrete
    print("\n[3️⃣ RESUMO POR TIPO DE LEMBRETE]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT reminder_minutes_before, COUNT(*) as count, SUM(CASE WHEN sent = 0 THEN 1 ELSE 0 END) as pending
        FROM match_reminders
        GROUP BY reminder_minutes_before
        ORDER BY reminder_minutes_before DESC
        """,
        []
    )
    
    reminder_stats = result.rows if result.rows else []
    
    if not reminder_stats:
        print("Nenhum lembrete no banco de dados")
    else:
        total_all = 0
        total_pending = 0
        
        for stat in reminder_stats:
            minutes = stat[0]
            count = stat[1]
            pending = stat[2]
            total_all += count
            total_pending += pending
            
            emoji = {
                0: "🔴",
                5: "🟡",
                15: "🟠",
                30: "🟡",
                60: "🔔"
            }.get(minutes, "❓")
            
            print(f"  {emoji} {minutes:2d} minutos: {count:3d} total | {pending:3d} pendentes")
        
        print("-" * 80)
        print(f"  📊 TOTAL: {total_all} lembretes | {total_pending} pendentes")
    
    # 4. Estatísticas de partidas
    print("\n[4️⃣ ESTATÍSTICAS DE PARTIDAS]")
    print("-" * 80)
    
    result = await client.execute(
        """
        SELECT COUNT(*) FROM matches_cache
        """,
        []
    )
    total_cached = result.rows[0][0] if result.rows else 0
    
    result = await client.execute(
        """
        SELECT COUNT(DISTINCT match_id) FROM match_reminders
        """,
        []
    )
    matches_with_reminders = result.rows[0][0] if result.rows else 0
    
    print(f"  📦 Total em cache: {total_cached} partidas")
    print(f"  📬 Com lembretes agendados: {matches_with_reminders} partidas")
    
    if total_cached > 0:
        percentage = (matches_with_reminders / total_cached) * 100
        print(f"  📊 Cobertura: {percentage:.1f}%")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
