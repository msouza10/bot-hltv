#!/usr/bin/env python3
"""
Script para monitorar lembretes em tempo real
Mostra quanto tempo falta para cada lembrete ser enviado
"""

import asyncio
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
    print("⏰ MONITORAMENTO DE LEMBRETES EM TEMPO REAL")
    print("=" * 80)
    print(f"\nHora atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Buscar próximos lembretes a vencer
    result = await client.execute(
        """
        SELECT 
            mr.id,
            mr.match_id,
            mr.reminder_minutes_before,
            mr.scheduled_time,
            mr.sent,
            mc.match_data
        FROM match_reminders mr
        LEFT JOIN matches_cache mc ON mr.match_id = mc.match_id
        WHERE mr.sent = 0
        ORDER BY mr.scheduled_time ASC
        LIMIT 20
        """,
        []
    )
    
    reminders = result.rows if result.rows else []
    
    if not reminders:
        print("❌ Nenhum lembrete pendente!")
        return
    
    print(f"📊 Próximos 20 lembretes pendentes:\n")
    
    now = datetime.now()
    
    for idx, reminder in enumerate(reminders, 1):
        reminder_id = reminder[0]
        match_id = reminder[1]
        minutes_before = reminder[2]
        scheduled_time_str = reminder[3]
        sent = reminder[4]
        
        scheduled_time = datetime.fromisoformat(scheduled_time_str)
        time_until = scheduled_time - now
        
        total_seconds = time_until.total_seconds()
        
        if total_seconds > 0:
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            status = "⏳ Aguardando"
            time_str = f"{minutes}m {seconds}s"
        else:
            status = "🚀 PRONTO PARA ENVIAR"
            time_str = "JÁ VENCIDO"
        
        print(f"{idx:2d}. {status}")
        print(f"    Partida: {match_id} | Tipo: {minutes_before}min")
        print(f"    Falta: {time_str}")
        print(f"    Agendado para: {scheduled_time.strftime('%H:%M:%S')}")
        print()
    
    # Contar quantos já venceram
    result = await client.execute(
        """
        SELECT COUNT(*) FROM match_reminders
        WHERE sent = 0 AND scheduled_time <= CURRENT_TIMESTAMP
        """,
        []
    )
    
    due_count = result.rows[0][0] if result.rows else 0
    
    print("\n" + "=" * 80)
    print(f"📈 RESUMO:")
    print(f"  • Total pendentes: {len(reminders)}")
    print(f"  • Já vencidos (prontos para enviar): {due_count}")
    print(f"  • Próximo em: {reminders[0][3] if reminders else 'N/A'}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
