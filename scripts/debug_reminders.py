"""
Debug script para verificar status dos lembretes no banco de dados.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager

async def check_reminders_status():
    """Verifica status dos lembretes no banco."""
    
    # Carregar variáveis de ambiente
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL', 'file:data/bot.db')
    
    cache_manager = MatchCacheManager(db_url)
    client = await cache_manager.get_client()
    
    print("\n" + "="*60)
    print("DEBUG: Status dos Lembretes")
    print("="*60)
    
    try:
        # 1. Verificar lembretes pendentes
        print("\n1️⃣  LEMBRETES PENDENTES (não enviados):")
        result = await client.execute(
            """
            SELECT id, guild_id, match_id, reminder_minutes_before, scheduled_time
            FROM match_reminders
            WHERE sent = 0
            ORDER BY scheduled_time ASC
            LIMIT 20
            """
        )
        
        if result.rows:
            for row in result.rows:
                reminder_id, guild_id, match_id, minutes_before, scheduled_time = row
                print(f"  • ID {reminder_id}: Match {match_id} | Guild {guild_id} | {minutes_before}min antes | Agendado: {scheduled_time}")
        else:
            print("  ⚠️  Nenhum lembrete pendente!")
        
        # 2. Verificar lembretes já enviados
        print("\n2️⃣  LEMBRETES JÁ ENVIADOS:")
        result = await client.execute(
            """
            SELECT COUNT(*) FROM match_reminders WHERE sent = 1
            """
        )
        sent_count = result.rows[0][0] if result.rows else 0
        print(f"  Total enviados: {sent_count}")
        
        # 3. Verificar lembretes que deveriam ter sido enviados (atrasados)
        print("\n3️⃣  LEMBRETES ATRASADOS (deveriam ter sido enviados):")
        now = datetime.now().isoformat()
        result = await client.execute(
            f"""
            SELECT id, guild_id, match_id, reminder_minutes_before, scheduled_time
            FROM match_reminders
            WHERE sent = 0 AND scheduled_time <= '{now}'
            ORDER BY scheduled_time DESC
            LIMIT 20
            """
        )
        
        if result.rows:
            print(f"  ⚠️  {len(result.rows)} lembretes não foram enviados no horário!")
            for row in result.rows[:5]:
                reminder_id, guild_id, match_id, minutes_before, scheduled_time = row
                print(f"    • ID {reminder_id}: Match {match_id} | {minutes_before}min | Deveria às: {scheduled_time}")
        else:
            print("  ✅ Todos os lembretes foram enviados no horário!")
        
        # 4. Resumo de lembretes por minuto
        print("\n4️⃣  DISTRIBUIÇÃO DE LEMBRETES PENDENTES:")
        result = await client.execute(
            """
            SELECT reminder_minutes_before, COUNT(*) as count
            FROM match_reminders
            WHERE sent = 0
            GROUP BY reminder_minutes_before
            ORDER BY reminder_minutes_before DESC
            """
        )
        
        if result.rows:
            total = sum(count for _, count in result.rows)
            print(f"  Total pendentes: {total}")
            for minutes_before, count in result.rows:
                print(f"    • {minutes_before} min antes: {count} lembretes")
        else:
            print("  Nenhum lembrete pendente")
        
        # 5. Verificar se há partidas no futuro
        print("\n5️⃣  PARTIDAS NO FUTURO:")
        result = await client.execute(
            f"""
            SELECT COUNT(*), COUNT(DISTINCT match_id)
            FROM matches_cache
            WHERE status IN ('not_started', 'running')
            AND begin_at > '{now}'
            """
        )
        
        if result.rows:
            total_matches, unique_matches = result.rows[0]
            print(f"  • {unique_matches} partidas futuras no cache")
        
        # 6. Verificar últimos eventos
        print("\n6️⃣  ÚLTIMOS EVENTOS NOS LOGS:")
        result = await client.execute(
            """
            SELECT timestamp, message FROM event_log
            ORDER BY timestamp DESC
            LIMIT 10
            """
        )
        
        if result.rows:
            for timestamp, message in result.rows:
                print(f"  {timestamp}: {message}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar lembretes: {e}")
    finally:
        await cache_manager.close()
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(check_reminders_status())
