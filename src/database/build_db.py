#!/usr/bin/env python3
"""
Script para criar/atualizar o banco de dados libSQL.
Uso: python -m src.database.build_db [--reset] [--stats]
"""

import asyncio
import argparse
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

import libsql_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar .env
load_dotenv()

# Configuração
DB_URL = os.getenv("LIBSQL_URL", "file:./data/bot.db")
AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def create_database():
    """Cria o banco de dados e aplica o schema."""
    
    logger.info(f"📄 Schema SQL: {SCHEMA_PATH}")
    logger.info(f"💾 Database URL: {DB_URL}")
    
    # Verificar se schema existe
    if not SCHEMA_PATH.exists():
        logger.error(f"❌ Arquivo schema.sql não encontrado em: {SCHEMA_PATH}")
        return False
    
    try:
        # Criar diretório se for arquivo local
        if DB_URL.startswith("file:"):
            db_path = DB_URL.replace("file:", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar ao banco
        if AUTH_TOKEN:
            client = libsql_client.create_client(url=DB_URL, auth_token=AUTH_TOKEN)
        else:
            client = libsql_client.create_client(url=DB_URL)
        
        logger.info("🔗 Conectado ao banco de dados")
        
        # Ler schema SQL
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        logger.info("📋 Aplicando schema...")
        
        # Dividir em statements individuais e executar
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                await client.execute(statement)
                logger.info(f"  ✓ Statement {i}/{len(statements)}")
            except Exception as e:
                # Ignorar erros de "table already exists"
                if "already exists" not in str(e):
                    logger.warning(f"  ⚠️ Statement {i}: {e}")
        
        await client.close()
        
        logger.info("✅ Banco de dados criado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco: {e}")
        import traceback
        traceback.print_exc()
        return False


async def reset_database():
    """Remove e recria o banco de dados."""
    
    logger.warning("⚠️  ATENÇÃO: Isso irá APAGAR TODOS OS DADOS!")
    
    # Se for arquivo local, deletar o arquivo
    if DB_URL.startswith("file:"):
        db_path = DB_URL.replace("file:", "")
        if Path(db_path).exists():
            Path(db_path).unlink()
            logger.info("🗑️  Banco de dados local removido")
    else:
        logger.error("❌ Reset não suportado para banco remoto via script")
        logger.info("💡 Use o dashboard do Turso para resetar banco remoto")
        return False
    
    return await create_database()


async def show_stats():
    """Mostra estatísticas do banco."""
    
    try:
        if AUTH_TOKEN:
            client = libsql_client.create_client(url=DB_URL, auth_token=AUTH_TOKEN)
        else:
            client = libsql_client.create_client(url=DB_URL)
        
        logger.info("\n📊 Estatísticas do Banco de Dados")
        logger.info("=" * 50)
        
        # Listar tabelas
        result = await client.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row["name"] for row in result.rows]
        logger.info(f"\n📋 Tabelas ({len(tables)}):")
        
        for table in tables:
            # Contar registros
            count_result = await client.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = count_result.rows[0]["count"]
            logger.info(f"  • {table}: {count} registros")
        
        # Views
        result = await client.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = [row["name"] for row in result.rows]
        
        if views:
            logger.info(f"\n👁️  Views ({len(views)}):")
            for view in views:
                logger.info(f"  • {view}")
        
        # Índices
        result = await client.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        indexes = [row["name"] for row in result.rows]
        
        if indexes:
            logger.info(f"\n🔍 Índices ({len(indexes)}):")
            for index in indexes:
                logger.info(f"  • {index}")
        
        # Tamanho do banco (apenas para arquivo local)
        if DB_URL.startswith("file:"):
            db_path = DB_URL.replace("file:", "")
            if Path(db_path).exists():
                size = Path(db_path).stat().st_size
                size_kb = size / 1024
                logger.info(f"\n💾 Tamanho: {size_kb:.1f} KB")
        
        logger.info("=" * 50 + "\n")
        
        await client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal."""
    
    parser = argparse.ArgumentParser(description="Gerenciar banco de dados libSQL")
    parser.add_argument("--reset", action="store_true", help="Remove e recria o banco")
    parser.add_argument("--stats", action="store_true", help="Mostra estatísticas do banco")
    
    args = parser.parse_args()
    
    logger.info("🚀 Build Database - libSQL")
    logger.info("")
    
    if args.reset:
        success = await reset_database()
    elif args.stats:
        success = await show_stats()
    else:
        success = await create_database()
    
    if success:
        if not args.stats:
            logger.info("\n💡 Dica: Use --stats para ver estatísticas do banco")
    else:
        logger.error("\n❌ Operação falhou!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
