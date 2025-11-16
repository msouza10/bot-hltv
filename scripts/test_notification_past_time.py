#!/usr/bin/env python3
"""
Script para testar notificações com horário passado (já deveria ter sido disparada).
Insere uma notificação com scheduled_time anterior ao tempo atual.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
import libsql_client

# Configuração do banco de dados
DB_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
DB_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

async def insert_past_notification():
    """Insere uma notificação com horário passado para teste"""
    
    # Conectar ao banco
    client = libsql_client.create_client(
        url=DB_URL,
        auth_token=DB_AUTH_TOKEN
    )
    
    # Usar um match_id que existe no banco (da execução anterior)
    match_id = 1269172
    guild_id = 1188166184760254594
    minutes_before = 0
    
    # Horário PASSADO (5 minutos atrás) - já deveria ter disparado
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║ 📝 Inserindo Notificação com Horário Passado
    ╠══════════════════════════════════════════════════════════════╣
    ║ Match ID:        {match_id}
    ║ Guild ID:        {guild_id}
    ║ Minutes Before:  {minutes_before}
    ║ Scheduled Time:  {past_time.isoformat()}
    ║ Status:          PENDENTE (not sent)
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Inserir na tabela match_reminders
        query = """
        INSERT INTO match_reminders 
        (guild_id, match_id, minutes_before, scheduled_time, sent_at)
        VALUES (?, ?, ?, ?, NULL)
        """
        
        result = await client.execute(
            query,
            [guild_id, match_id, minutes_before, past_time.isoformat()]
        )
        
        print(f"✅ Notificação inserida com sucesso!")
        print(f"   Registros afetados: {result.rows_affected if hasattr(result, 'rows_affected') else 'N/A'}")
        
        # Verificar se foi inserida
        verify = await client.execute(
            """
            SELECT id, guild_id, match_id, minutes_before, scheduled_time, sent_at
            FROM match_reminders 
            WHERE guild_id = ? AND match_id = ? AND minutes_before = ?
            ORDER BY id DESC LIMIT 1
            """,
            [guild_id, match_id, minutes_before]
        )
        
        if verify.rows:
            row = verify.rows[0]
            print(f"\n✅ Verificação:")
            print(f"   ID Reminder:     {row[0]}")
            print(f"   Guild:           {row[1]}")
            print(f"   Match:           {row[2]}")
            print(f"   Minutes Before:  {row[3]}")
            print(f"   Scheduled:       {row[4]}")
            print(f"   Sent At:         {row[5]}")
            print(f"\n🔍 Status: PENDENTE (precisa ser disparada!)")
            print(f"⏰ O bot deve detectar e disparar esta notificação no próximo ciclo.")
        
    except Exception as e:
        print(f"❌ Erro ao inserir: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(insert_past_notification())
