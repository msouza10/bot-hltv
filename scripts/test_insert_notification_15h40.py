#!/usr/bin/env python3
"""
Script para inserir manualmente uma notificação com horário 15h40.
Testa se o sistema detecta e dispara notificações.
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
TESTING_GUILD_ID = int(os.getenv("TESTING_GUILD_ID", "1188166184760254594"))

async def insert_notification():
    """Insere uma notificação com scheduled_time = 15:40"""
    
    cache_manager = MatchCacheManager(LIBSQL_URL, LIBSQL_AUTH_TOKEN)
    client = await cache_manager.get_client()
    
    logger.info("=" * 80)
    logger.info("🧪 TESTE: Inserindo notificação para 15h40")
    logger.info("=" * 80)
    
    # 1. Buscar um match para usar
    logger.info("\n📍 PASSO 1: Buscando um match para usar...")
    result = await client.execute(
        """
        SELECT match_id, match_data 
        FROM matches_cache 
        WHERE status = 'not_started'
        LIMIT 1
        """,
        []
    )
    
    if not result.rows:
        logger.error("❌ Nenhum match encontrado!")
        return
    
    match_id = result.rows[0][0]
    logger.info(f"✅ Match encontrado: {match_id}")
    
    # 2. Calcular timestamp para 15:40
    logger.info("\n📍 PASSO 2: Calculando timestamp para 15:40...")
    target_time = datetime.now().replace(hour=15, minute=40, second=0, microsecond=0)
    target_time_str = target_time.isoformat()
    
    time_diff = (datetime.now() - target_time).total_seconds()
    logger.info(f"✅ Timestamp alvo: {target_time_str}")
    logger.info(f"   (diferença: {time_diff:.0f} segundos)")
    
    # 3. Inserir notificação
    logger.info("\n📍 PASSO 3: Inserindo notificação no banco...")
    
    await client.execute(
        """
        INSERT INTO match_reminders 
        (guild_id, match_id, reminder_minutes_before, scheduled_time, sent)
        VALUES (?, ?, ?, ?, ?)
        """,
        [TESTING_GUILD_ID, match_id, 30, target_time_str, 0]
    )
    
    logger.info(f"✅ Notificação inserida!")
    
    # 4. Verificar
    logger.info("\n📍 PASSO 4: Verificando inserção...")
    result = await client.execute(
        """
        SELECT id, guild_id, match_id, reminder_minutes_before, scheduled_time, sent
        FROM match_reminders
        WHERE match_id = ? AND reminder_minutes_before = 30 AND scheduled_time = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        [match_id, target_time_str]
    )
    
    if result.rows:
        row = result.rows[0]
        logger.info(f"✅ Notificação gravada com sucesso:")
        logger.info(f"   ID: {row[0]}")
        logger.info(f"   Guild: {row[1]}")
        logger.info(f"   Match: {row[2]}")
        logger.info(f"   Minutos antes: {row[3]}")
        logger.info(f"   Agendado para: {row[4]}")
        logger.info(f"   Enviado: {row[5]}")
    
    # 5. Instruções finais
    logger.info("\n" + "=" * 80)
    logger.info("✅ PRONTO PARA TESTAR!")
    logger.info("=" * 80)
    logger.info("\n📌 PRÓXIMAS AÇÕES:")
    logger.info("   1. Inicie o bot: venv/bin/python -m src.bot")
    logger.info("   2. A notificação será detectada na próxima verificação")
    logger.info("      (que ocorre a cada 1 minuto)")
    logger.info("   3. Observe a mensagem aparecer no Discord!")
    logger.info("   4. Verifique os logs para confirmar envio\n")

if __name__ == "__main__":
    asyncio.run(insert_notification())
