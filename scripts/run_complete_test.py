#!/usr/bin/env python3
"""
Script para executar teste completo em sequência:
1. Reset do banco
2. Execução do bot por um tempo
3. Teste com dados reais
"""

import asyncio
import subprocess
import time
import os
import signal
import sys

print("\n" + "="*80)
print("🚀 TESTE COMPLETO - YouTube Service Integration")
print("="*80)

# Step 1: Reset do banco
print("\n[1/3] 🗑️  Limpando banco de dados...")
try:
    os.remove("data/bot.db")
    print("     ✅ Banco resetado")
except FileNotFoundError:
    print("     ℹ️  Banco não existia (criará novo)")

# Step 2: Inicializar banco
print("\n[2/3] 🏗️  Inicializando banco de dados...")
result = subprocess.run(
    ["python", "-m", "src.database.build_db"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("     ✅ Banco inicializado")
else:
    print(f"     ❌ Erro ao inicializar: {result.stderr}")
    sys.exit(1)

# Step 3: Executar bot por um tempo
print("\n[3/3] 🤖 Rodando bot por 30 segundos para popular o banco...")
print("     (O bot coletará dados de partidas ao vivo)")

bot_process = subprocess.Popen(
    ["python", "-m", "src.bot"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Aguardar 30 segundos
try:
    print("     ⏳ Aguardando coleta de dados...")
    for i in range(30, 0, -1):
        print(f"     ⏱️  {i}s restantes...", end="\r")
        time.sleep(1)
    
    print("     ✅ Tempo de coleta concluído")
    
except KeyboardInterrupt:
    print("\n     ⏹️  Interrompido pelo usuário")

# Encerrar bot
print("\n     🛑 Encerrando bot...")
bot_process.terminate()
try:
    bot_process.wait(timeout=5)
except subprocess.TimeoutExpired:
    bot_process.kill()
    bot_process.wait()
print("     ✅ Bot encerrado")

# Step 4: Executar testes
print("\n" + "="*80)
print("✅ INICIANDO TESTES")
print("="*80)

result = subprocess.run(
    ["python", "scripts/test_youtube_real_data.py"],
    capture_output=False
)

sys.exit(result.returncode)
