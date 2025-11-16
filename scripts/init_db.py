"""
Script para inicializar o banco de dados com o schema
"""

import libsql_client
import asyncio

async def init_db():
    # Ler schema com encoding UTF-8
    with open('src/database/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Criar cliente
    client = libsql_client.create_client(url='file:./data/bot.db')
    
    # Executar cada comando SQL separadamente
    for statement in schema.split(';'):
        statement = statement.strip()
        if statement:
            try:
                await client.execute(statement)
                print(f'✓ {statement[:60]}...')
            except Exception as e:
                if 'already exists' not in str(e):
                    print(f'✗ Erro: {e}')

asyncio.run(init_db())
print('✓ Schema executado com sucesso!')
