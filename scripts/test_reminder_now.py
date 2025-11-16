#!/usr/bin/env python3
"""
Script para testar lembretes agora mesmo.
Força um lembrete para ser executado nos próximos 30 segundos.
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
import logging

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.cache_manager import MatchCacheManager
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

LIBSQL_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")

async def test_reminder():
    """Testa um lembrete agora mesmo."""
    
    cache_manager = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    client = await cache_manager.get_client()
    
    logger.info("=" * 80)
    logger.info("🧪 TESTE DE LEMBRETES - Simulando agendamento para 04:40")
    logger.info("=" * 80)
    
    # 1. Buscar um lembrete pendente
    logger.info("\n📍 PASSO 1: Buscando lembretes pendentes...")
    result = await client.execute(
        """
        SELECT mr.id, mr.guild_id, mr.match_id, mr.reminder_minutes_before,
               mr.scheduled_time, mc.match_data
        FROM match_reminders mr
        JOIN matches_cache mc ON mr.match_id = mc.match_id
        WHERE mr.sent = 0
        LIMIT 1
        """,
        []
    )
    
    if not result.rows:
        logger.error("❌ Nenhum lembrete pendente encontrado!")
        return
    
    reminder = result.rows[0]
    reminder_id = reminder[0]
    guild_id = reminder[1]
    match_id = reminder[2]
    minutes_before = reminder[3]
    scheduled_time_str = reminder[4]
    
    logger.info(f"✅ Encontrado: ID {reminder_id}")
    logger.info(f"   Guild: {guild_id}")
    logger.info(f"   Match: {match_id}")
    logger.info(f"   Minutos: {minutes_before}")
    logger.info(f"   Agendado para: {scheduled_time_str}")
    
    # 2. Atualizar para agora (04:40)
    logger.info("\n📍 PASSO 2: Atualizando para 04:40 (agora!)...")
    now = datetime.now()
    target_time = now.replace(hour=4, minute=40, second=0)
    
    # Se já passou das 04:40, usar o horário atual
    if now > target_time:
        target_time = now - timedelta(seconds=5)  # 5 segundos atrás
    
    target_time_str = target_time.isoformat()
    
    logger.info(f"✅ Novo horário: {target_time_str}")
    
    await client.execute(
        """
        UPDATE match_reminders 
        SET scheduled_time = ?
        WHERE id = ?
        """,
        [target_time_str, reminder_id]
    )
    
    logger.info(f"✅ Lembrete {reminder_id} agora vence em {target_time_str}")
    
    # 3. Informar para o usuário
    logger.info("\n" + "=" * 80)
    logger.info("✅ PRONTO! O lembrete foi agendado para agora!")
    logger.info("=" * 80)
    logger.info("\n📌 PRÓXIMAS AÇÕES:")
    logger.info("   1. Aguarde 1 minuto até a próxima verificação de lembretes")
    logger.info("   2. Você verá nos logs:")
    logger.info(f"      - 🚀 ENVIANDO AGORA: Match {match_id} | {minutes_before}min antes")
    logger.info(f"      - [NOTIF-SUCCESS] ✅ ENVIADA COM SUCESSO!")
    logger.info("   3. Você também verá a mensagem no Discord!")
    logger.info("\n💡 Dica: Os logs devem aparecer em menos de 1 minuto.\n")

if __name__ == "__main__":
    asyncio.run(test_reminder())
