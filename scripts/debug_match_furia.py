#!/usr/bin/env python3
"""
Script para debugar por quê uma partida específica não foi notificada.
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

MATCH_ID = 1261044  # FURIA vs Team Falcons

async def debug_match():
    db_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    auth_token = os.getenv("LIBSQL_AUTH_TOKEN")
    
    cache_manager = MatchCacheManager(db_url, auth_token)
    client = await cache_manager.get_client()
    
    print("\n" + "=" * 80)
    print(f"🔍 DEBUG PARTIDA ID {MATCH_ID} - FURIA vs Team Falcons")
    print("=" * 80 + "\n")
    
    # 1. Verificar dados no cache
    print("[1️⃣ DADOS NA CACHE]")
    print("-" * 80)
    
    result = await client.execute(
        f"""
        SELECT match_id, status, begin_at, match_data
        FROM matches_cache
        WHERE match_id = {MATCH_ID}
        """,
        []
    )
    
    if not result.rows:
        print(f"❌ Partida {MATCH_ID} NÃO está no cache!")
        print("   Solução: Aguarde a próxima sincronização do cache (a cada 15 min)")
        await client.close()
        return
    
    row = result.rows[0]
    match_id, status, begin_at, match_data_json = row
    
    print(f"✅ Partida encontrada no cache!")
    print(f"   • ID: {match_id}")
    print(f"   • Status: {status}")
    print(f"   • Begin_at: {begin_at}")
    
    # Parse dados
    if match_data_json:
        try:
            match_data = json.loads(match_data_json)
            league = match_data.get('league', {}).get('name', '?')
            opponents = match_data.get('opponents', [])
            teams = []
            for opp in opponents:
                if opp.get('opponent'):
                    teams.append(opp['opponent'].get('name', '?'))
            print(f"   • Torneio: {league}")
            print(f"   • Times: {' vs '.join(teams)}")
        except:
            pass
    
    # 2. Verificar se foi pulada no agendamento
    print("\n[2️⃣ MOTIVO DE NÃO AGENDAR]")
    print("-" * 80)
    
    if status not in ['not_started', 'running']:
        print(f"❌ STATUS INVÁLIDO: '{status}'")
        print(f"   Motivo: Apenas 'not_started' ou 'running' são agendados")
        print(f"   Solução: Nenhuma (partida já começou ou foi cancelada)")
        await client.close()
        return
    
    if not begin_at:
        print(f"❌ SEM BEGIN_AT")
        print(f"   Motivo: Partida não tem horário de início definido")
        print(f"   Solução: Aguarde a API atualizar o horário")
        await client.close()
        return
    
    print(f"✅ Status e horário OK - deveria ter sido agendada!")
    
    # 3. Verificar se há lembretes agendados
    print("\n[3️⃣ LEMBRETES AGENDADOS]")
    print("-" * 80)
    
    result = await client.execute(
        f"""
        SELECT id, reminder_minutes_before, scheduled_time, sent, sent_at
        FROM match_reminders
        WHERE match_id = {MATCH_ID}
        ORDER BY reminder_minutes_before DESC
        """,
        []
    )
    
    reminders = result.rows if result.rows else []
    
    if not reminders:
        print(f"❌ NENHUM LEMBRETE AGENDADO!")
        print(f"   Solução: Execute /notificacoes ativar:true novamente")
        await client.close()
        return
    
    print(f"✅ {len(reminders)} lembretes agendados:")
    
    now = datetime.now()
    for reminder in reminders:
        reminder_id, minutes_before, scheduled_time_str, sent, sent_at = reminder
        scheduled_time = datetime.fromisoformat(scheduled_time_str)
        
        time_until = scheduled_time - now
        
        if sent:
            status_emoji = "✅ ENVIADO"
            extra = f"em {sent_at}"
        elif time_until.total_seconds() <= 0:
            status_emoji = "🚀 PRONTO"
            extra = "aguardando loop"
        else:
            seconds = int(time_until.total_seconds())
            minutes_left = seconds // 60
            secs_left = seconds % 60
            status_emoji = "⏳ AGUARDANDO"
            extra = f"faltam {minutes_left}m {secs_left}s"
        
        print(f"   • {minutes_before:2d}min antes: {status_emoji} - {extra}")
    
    # 4. Dicas
    print("\n[4️⃣ RESUMO E PRÓXIMAS AÇÕES]")
    print("-" * 80)
    
    if reminders and all(r[3] for r in reminders):  # All sent
        print("✅ Todos os lembretes foram enviados!")
    elif reminders and any(r[4] for r in reminders):  # Some have sent_at
        print("✅ Alguns lembretes foram enviados!")
        print("   Se a notificação de 1h não chegou, a partida pode ter:")
        print("   - Começado mais cedo")
        print("   - Mudado de horário")
        print("   - Sido cancelada")
    elif reminders:
        print("⏳ Lembretes agendados mas ainda não enviados")
        print("   Aguarde o horário do lembrete (o bot verifica a cada 1 minuto)")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(debug_match())
