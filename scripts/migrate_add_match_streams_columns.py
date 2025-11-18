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
    "is_automated": "BOOLEAN DEFAULT 0",
    "viewer_count": "INTEGER DEFAULT 0",
    "title": "TEXT"
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

    # Obter colunas via PRAGMA (libsql suporta PRAGMA via execute)
    result = await client.execute("PRAGMA table_info(match_streams);")
    existing = [row['name'] for row in result.rows]

    to_add = {k: v for k, v in REQUIRED_COLUMNS.items() if k not in existing}
    if not to_add:
        logger.info("Nenhuma coluna faltante encontrada em match_streams (libsql).")
        await client.close()
        return True

    for col, definition in to_add.items():
        stmt = f"ALTER TABLE match_streams ADD COLUMN {col} {definition};"
        try:
            await client.execute(stmt)
            logger.info(f"Coluna adicionada: {col}")
        except Exception as e:
            logger.error(f"Falha ao adicionar coluna {col}: {e}")
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
    try:
        existing = get_columns_sqlite(conn, 'match_streams')
    except Exception as e:
        logger.error(f"Erro ao obter informações da tabela: {e}")
        conn.close()
        return False

    to_add = {k: v for k, v in REQUIRED_COLUMNS.items() if k not in existing}
    if not to_add:
        logger.info("Nenhuma coluna faltante encontrada em match_streams (sqlite local).")
        conn.close()
        return True

    for col, definition in to_add.items():
        try:
            add_column_sqlite(conn, 'match_streams', col, definition)
            logger.info(f"Coluna adicionada: {col}")
        except Exception as e:
            logger.error(f"Falha ao adicionar coluna {col}: {e}")
            conn.close()
            return False

    conn.close()
    logger.info("Migração concluída (sqlite local)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Migração de colunas em match_streams")
    parser.add_argument('--db', default=os.getenv('LIBSQL_URL', 'file:./data/bot.db'), help='DB URL (padrão file:./data/bot.db)')
    args = parser.parse_args()

    db_url = args.db
    if db_url.startswith('file:'):
        db_path = db_url.replace('file:', '')
        logger.info(f"DB local detectado: {db_path}")
        ok = migrate_sqlite(db_path)
        if ok:
            logger.info('Migração finalizada com sucesso.')
        else:
            logger.error('Migração falhou.')
    else:
        # libsql URL
        import asyncio
        logger.info(f"DB remoto detectado: {db_url}")
        ok = asyncio.run(migrate_libsql(db_url))
        if ok:
            logger.info('Migração finalizada com sucesso (libsql).')
        else:
            logger.error('Migração falhou (libsql).')


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Migration: Ensure `match_streams` table has `is_automated`, `viewer_count`, `title` columns.
Usage (safe):
  ./venv/bin/python scripts/migrate_add_match_streams_columns.py --db file:./data/bot.db --backup

This will:
- Backup the DB file to data/bot.db.bak (only for file: local path)
- Connect via libsql_client and check PRAGMA table_info(match_streams)
- Add missing columns via `ALTER TABLE` if necessary
- Print actions
"""

import argparse
import shutil
import sys
from pathlib import Path

import libsql_client


MIGRATIONS = [
    ("is_automated", "BOOLEAN", "DEFAULT 0"),
    ("viewer_count", "INTEGER", "DEFAULT 0"),
    ("title", "TEXT", "")
]


def parse_args():
    p = argparse.ArgumentParser(description="Migrate match_streams columns")
    p.add_argument("--db", default="file:./data/bot.db", help="libsql url or file: local path")
    p.add_argument("--backup", action="store_true", help="Backup local DB file before migration (if file:) ")
    return p.parse_args()


async def run_migration(db_url: str, backup: bool):
    # If file local, optionally backup
    if db_url.startswith("file:") and backup:
        db_path = db_url.replace("file:", "")
        db_file = Path(db_path)
        if db_file.exists():
            backup_path = db_file.with_suffix(db_file.suffix + ".bak")
            print(f"Backing up local DB: {db_file} -> {backup_path}")
            shutil.copyfile(db_file, backup_path)
        else:
            print("Local DB file not found; continuing without backup")

    client = libsql_client.create_client(url=db_url)

    # Get existing columns
    result = await client.execute("PRAGMA table_info(match_streams)")
    existing_cols = [row[1] for row in result.rows]  # row format: (cid, name, type, notnull, dflt_value, pk)
    print("Existing columns:", existing_cols)

    # For each migration column, add if missing
    added_any = False
    for name, col_type, default_clause in MIGRATIONS:
        if name in existing_cols:
            print(f"Column '{name}' already exists; skipping")
            continue
        statement = f"ALTER TABLE match_streams ADD COLUMN {name} {col_type} {default_clause}".strip()
        print(f"Adding column with: {statement}")
        try:
            await client.execute(statement)
            print(f"  ✓ Column '{name}' added")
            added_any = True
        except Exception as e:
            print(f"  ✗ Failed to add column '{name}': {e}")

    if not added_any:
        print("No columns required adding.")

    await client.close()


if __name__ == "__main__":
    args = parse_args()
    import asyncio

    try:
        asyncio.run(run_migration(args.db, args.backup))
    except Exception as e:
        print("Migration failed:", e)
        sys.exit(1)

    print("Migration finished.")
