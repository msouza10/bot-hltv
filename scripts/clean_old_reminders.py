#!/usr/bin/env python3
"""
Script para limpar lembretes antigos (antes do fix de timezone).
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.cache_manager import MatchCacheManager

load_dotenv()

async def clean_old_reminders():
    db_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    auth_token = os.getenv("LIBSQL_AUTH_TOKEN")
    
    cache_manager = MatchCacheManager(db_url, auth_token)
    client = await cache_manager.get_client()
    
    print("\n" + "=" * 80)
    print("🧹 LIMPANDO LEMBRETES ANTIGOS (com horários incorretos)")
    print("=" * 80 + "\n")
    
    # Buscar todos os lembretes não enviados
    result = await client.execute(
        """
        SELECT COUNT(*) FROM match_reminders WHERE sent = 0
        """,
        []
    )
    
    total = result.rows[0][0] if result.rows else 0
    
    print(f"📊 Total de lembretes pendentes: {total}")
    
    if total == 0:
        print("✅ Nenhum lembrete para limpar")
        await client.close()
        return
    
    # Deletar todos os lembretes não enviados
    print(f"\n🗑️ Deletando {total} lembretes não enviados...")
    await client.execute(
        "DELETE FROM match_reminders WHERE sent = 0",
        []
    )
    
    print(f"✅ {total} lembretes deletados!")
    
    # Verificar quantos restaram
    result = await client.execute(
        """
        SELECT COUNT(*) FROM match_reminders
        """,
        []
    )
    
    remaining = result.rows[0][0] if result.rows else 0
    
    print(f"\n📊 Lembretes restantes (já enviados): {remaining}")
    
    print("\n" + "=" * 80)
    print("✅ PRÓXIMAS AÇÕES:")
    print("=" * 80)
    print("1. Reinicie o bot")
    print("2. Execute /notificacoes ativar:true novamente")
    print("3. Os lembretes serão agendados com horários CORRETOS agora!")
    print("=" * 80 + "\n")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(clean_old_reminders())
