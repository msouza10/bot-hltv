#!/usr/bin/env python3
"""
Script de migração: adiciona colunas ausentes na tabela `match_streams`.

Uso:
  python scripts/migrate_add_match_streams_columns.py [--db file:./data/bot.db]

Funcionalidades:
- Detecta colunas faltantes: `is_automated`, `viewer_count`, `title` e as adiciona.
- Suporta DB local (file:./data/bot.db) e remota (libSQL URL) via libsql_client.
- Faz backup do DB local antes de alterar.
"""
import argparse
import os
import shutil
import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


REQUIRED_COLUMNS = {
    "match_streams": {
        "is_automated": "BOOLEAN DEFAULT 0",
        "viewer_count": "INTEGER DEFAULT 0",
        "title": "TEXT"
    },
    "guild_config": {
        # Timezone column expected by the bot
        "timezone": "TEXT DEFAULT 'America/Sao_Paulo'"
    }
}


def backup_local_db(db_path: str) -> str:
    ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    backup = f"{db_path}.bak.{ts}"
    shutil.copy2(db_path, backup)
    logger.info(f"Backup criado: {backup}")
    return backup


def get_columns_sqlite(conn: sqlite3.Connection, table: str):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table});")
    rows = cursor.fetchall()
    return [row[1] for row in rows]


def add_column_sqlite(conn: sqlite3.Connection, table: str, column: str, definition: str):
    stmt = f"ALTER TABLE {table} ADD COLUMN {column} {definition};"
    logger.info(f"Executando: {stmt}")
    conn.execute(stmt)
    conn.commit()


async def migrate_libsql(url: str):
    try:
        import libsql_client
    except Exception:
        logger.error("libsql_client não disponível. Instale as dependências no ambiente remoto.")
        return False

    # Conectar com libsql
    client = libsql_client.create_client(url=url, auth_token=os.getenv('LIBSQL_AUTH_TOKEN')) if os.getenv('LIBSQL_AUTH_TOKEN') else libsql_client.create_client(url=url)

    # Migrate each table as in SQLite
    for table, cols in REQUIRED_COLUMNS.items():
        try:
            result = await client.execute(f"PRAGMA table_info({table});")
            existing = [row["name"] for row in result.rows]
        except Exception as e:
            logger.warning(f"Tabela {table} não existe no DB remoto: {e}")
            continue

        to_add = {k: v for k, v in cols.items() if k not in existing}
        if not to_add:
            logger.info(f"Nenhuma coluna faltante encontrada em {table} (libsql).")
            continue

        for col, definition in to_add.items():
            stmt = f"ALTER TABLE {table} ADD COLUMN {col} {definition};"
            try:
                await client.execute(stmt)
                logger.info(f"Coluna adicionada: {table}.{col}")
            except Exception as e:
                logger.error(f"Falha ao adicionar coluna {table}.{col}: {e}")
                await client.close()
                return False

    await client.close()
    logger.info("Migração concluída (libsql)")
    return True


def migrate_sqlite(db_path: str) -> bool:
    if not os.path.exists(db_path):
        logger.error(f"Arquivo de banco não existe: {db_path}")
        return False

    backup_local_db(db_path)

    conn = sqlite3.connect(db_path)
    # migrate each table defined in REQUIRED_COLUMNS
    tables = list(REQUIRED_COLUMNS.keys())
    for table in tables:
        try:
            existing = get_columns_sqlite(conn, table)
        except Exception as e:
            logger.warning(f"Tabela {table} não existe no DB local: {e}")
            continue

        to_add = {k: v for k, v in REQUIRED_COLUMNS[table].items() if k not in existing}
        if not to_add:
            logger.info(f"Nenhuma coluna faltante encontrada em {table} (sqlite local).")
            continue

        for col, definition in to_add.items():
            try:
                add_column_sqlite(conn, table, col, definition)
                logger.info(f"Coluna adicionada: {table}.{col}")
            except Exception as e:
                logger.error(f"Falha ao adicionar coluna {table}.{col}: {e}")
                conn.close()
                return False

    conn.close()
    logger.info("Migração concluída (sqlite local)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Migração de colunas em match_streams/guild_config")
    parser.add_argument('--db', default=os.getenv('LIBSQL_URL', 'file:./data/bot.db'), help='DB URL (padrão file:./data/bot.db)')
    parser.add_argument('--backup', action='store_true', help='Criar backup do DB local antes da alteração (somente file:)')
    parser.add_argument('--dry-run', action='store_true', help='Não aplica mudanças; apenas lista colunas faltantes')
    args = parser.parse_args()

    db_url = args.db
    if db_url.startswith('file:'):
        db_path = db_url.replace('file:', '')
        logger.info(f"DB local detectado: {db_path}")
        if args.dry_run:
            # only list missing columns
            missing = False
            conn = sqlite3.connect(db_path)
            for table, cols in REQUIRED_COLUMNS.items():
                try:
                    existing = get_columns_sqlite(conn, table)
                except Exception as e:
                    logger.warning(f"Tabela {table} não existe no DB local: {e}")
                    continue
                for col in cols.keys():
                    if col not in existing:
                        logger.info(f"Falta coluna: {table}.{col}")
                        missing = True
            conn.close()
            if not missing:
                logger.info("Nenhuma coluna faltante encontrada em DB local.")
            return

        ok = migrate_sqlite(db_path)
        if ok:
            logger.info('Migração finalizada com sucesso.')
        else:
            logger.error('Migração falhou.')
    else:
        # libsql URL
        import asyncio
        logger.info(f"DB remoto detectado: {db_url}")
        if args.dry_run:
            async def dry_check():
                try:
                    import libsql_client
                except Exception:
                    logger.error("libsql_client não disponível; instale as dependências no ambiente remoto.")
                    return
                client = libsql_client.create_client(url=db_url, auth_token=os.getenv('LIBSQL_AUTH_TOKEN')) if os.getenv('LIBSQL_AUTH_TOKEN') else libsql_client.create_client(url=db_url)
                for table, cols in REQUIRED_COLUMNS.items():
                    try:
                        result = await client.execute(f"PRAGMA table_info({table});")
                        existing = [row['name'] for row in result.rows]
                    except Exception as e:
                        logger.warning(f"Tabela {table} não existe no DB remoto: {e}")
                        continue
                    for col in cols.keys():
                        if col not in existing:
                            logger.info(f"Falta coluna remota: {table}.{col}")
                await client.close()
            asyncio.run(dry_check())
            return

        ok = asyncio.run(migrate_libsql(db_url))
        if ok:
            logger.info('Migração finalizada com sucesso (libsql).')
        else:
            logger.error('Migração falhou (libsql).')


if __name__ == '__main__':
    main()
