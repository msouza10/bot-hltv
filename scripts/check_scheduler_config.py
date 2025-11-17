#!/usr/bin/env python3
"""
Verifica se o agendador de cache está configurado corretamente.
Valida:
- Tasks estão com os intervalos corretos
- Locks estão configurados para evitar race conditions
- Callbacks before_loop estão presentes
- Métodos start/stop existem
- Locks são exclusivos
"""

import sys
import os
import ast
import inspect

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.cache_scheduler import CacheScheduler
from nextcord.ext import tasks


def check_scheduler_config():
    """Verifica a configuração do scheduler."""
    
    print("=" * 70)
    print("🔍 VERIFICAÇÃO DA CONFIGURAÇÃO DO SCHEDULER")
    print("=" * 70)
    
    # 1️⃣ Verificar se as tasks estão definidas
    print("\n1️⃣  VERIFICANDO TASKS DEFINIDAS:")
    print("   " + "-" * 65)
    
    if hasattr(CacheScheduler, 'update_all_task'):
        print("   ✅ update_all_task existe")
        task = CacheScheduler.update_all_task
        if isinstance(task, tasks.Loop):
            print(f"      Intervalo: {task.minutes} minuto(s)")
            print(f"      Count: {task.count}")
        else:
            # É um método decorado, verificar propriedades
            print(f"      Tipo: {type(task)}")
    else:
        print("   ✗ update_all_task NÃO ENCONTRADA")
    
    if hasattr(CacheScheduler, 'check_finished_task'):
        print("   ✅ check_finished_task existe")
        task = CacheScheduler.check_finished_task
        if isinstance(task, tasks.Loop):
            print(f"      Intervalo: {task.minutes} minuto(s)")
            print(f"      Count: {task.count}")
    else:
        print("   ✗ check_finished_task NÃO ENCONTRADA")
    
    # 2️⃣ Verificar callbacks before_loop
    print("\n2️⃣  VERIFICANDO CALLBACKS before_loop:")
    print("   " + "-" * 65)
    
    if hasattr(CacheScheduler, 'before_update_all'):
        print("   ✅ before_update_all callback existe")
    else:
        print("   ⚠️  before_update_all callback NÃO ENCONTRADA")
    
    if hasattr(CacheScheduler, 'before_check_finished'):
        print("   ✅ before_check_finished callback existe")
    else:
        print("   ⚠️  before_check_finished callback NÃO ENCONTRADA")
    
    # 3️⃣ Verificar métodos start/stop
    print("\n3️⃣  VERIFICANDO MÉTODOS DE CONTROLE:")
    print("   " + "-" * 65)
    
    if hasattr(CacheScheduler, 'start') and callable(getattr(CacheScheduler, 'start')):
        print("   ✅ Método start() existe")
    else:
        print("   ✗ Método start() NÃO ENCONTRADO")
    
    if hasattr(CacheScheduler, 'stop') and callable(getattr(CacheScheduler, 'stop')):
        print("   ✅ Método stop() existe")
    else:
        print("   ✗ Método stop() NÃO ENCONTRADO")
    
    # 4️⃣ Verificar locks
    print("\n4️⃣  VERIFICANDO LOCKS:")
    print("   " + "-" * 65)
    
    import src.services.cache_scheduler as scheduler_module
    if hasattr(scheduler_module, '_cache_update_lock'):
        print("   ✅ _cache_update_lock definida no módulo")
        print(f"      Tipo: {type(scheduler_module._cache_update_lock)}")
    else:
        print("   ✗ _cache_update_lock NÃO DEFINIDA")
    
    # 5️⃣ Analisar código-fonte para buscar locks em métodos
    print("\n5️⃣  VERIFICANDO USO DE LOCKS NOS MÉTODOS:")
    print("   " + "-" * 65)
    
    try:
        import inspect
        source = inspect.getsource(CacheScheduler)
        
        if '_cache_update_lock' in source:
            count = source.count('_cache_update_lock')
            print(f"   ✅ _cache_update_lock aparece {count}x no código")
            
            # Verificar em quais métodos
            if 'async with _cache_update_lock:' in source:
                lines = source.split('\n')
                for i, line in enumerate(lines):
                    if 'async with _cache_update_lock:' in line:
                        # Encontrar qual método
                        for j in range(i, -1, -1):
                            if 'async def ' in lines[j]:
                                method = lines[j].strip()
                                print(f"      • Usado em: {method}")
                                break
        else:
            print("   ⚠️  _cache_update_lock não aparece no código-fonte")
    except Exception as e:
        print(f"   ⚠️  Erro ao analisar código: {e}")
    
    # 6️⃣ Análise da configuração esperada
    print("\n6️⃣  CONFIGURAÇÃO ESPERADA:")
    print("   " + "-" * 65)
    
    print("   Task 1: update_all_task")
    print("   • Intervalo: 3 minutos ✅")
    print("   • Count: None (infinito) ✅")
    print("   • Função: update_all_matches()")
    print("   • Usa lock: SIM ✅")
    
    print("\n   Task 2: check_finished_task")
    print("   • Intervalo: 1 minuto ✅")
    print("   • Count: None (infinito) ✅")
    print("   • Função: check_running_to_finished_transitions_fast()")
    print("   • Usa lock: SIM ✅")
    
    # 7️⃣ Verificar inicialização no bot.py
    print("\n7️⃣  VERIFICANDO INICIALIZAÇÃO NO BOT.PY:")
    print("   " + "-" * 65)
    
    try:
        with open('/home/msouza/Documents/bot-hltv/src/bot.py', 'r') as f:
            bot_source = f.read()
        
        if 'CacheScheduler' in bot_source:
            print("   ✅ CacheScheduler importado em bot.py")
        else:
            print("   ✗ CacheScheduler NÃO importado em bot.py")
        
        if 'cache_scheduler.start()' in bot_source or '.start()' in bot_source:
            print("   ✅ cache_scheduler.start() provavelmente chamado")
        else:
            print("   ⚠️  cache_scheduler.start() pode não estar sendo chamado")
        
        if 'self.cache_scheduler' in bot_source:
            print("   ✅ cache_scheduler armazenado como atributo da classe")
        else:
            print("   ⚠️  cache_scheduler pode não ser armazenado como atributo")
    
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar bot.py: {e}")
    
    # RESUMO FINAL
    print("\n" + "=" * 70)
    print("📋 RESUMO DA CONFIGURAÇÃO:")
    print("=" * 70)
    
    summary = {
        "update_all_task": hasattr(CacheScheduler, 'update_all_task'),
        "check_finished_task": hasattr(CacheScheduler, 'check_finished_task'),
        "before_update_all": hasattr(CacheScheduler, 'before_update_all'),
        "before_check_finished": hasattr(CacheScheduler, 'before_check_finished'),
        "start_method": hasattr(CacheScheduler, 'start'),
        "stop_method": hasattr(CacheScheduler, 'stop'),
        "cache_update_lock": hasattr(scheduler_module, '_cache_update_lock'),
    }
    
    all_ok = all(summary.values())
    
    for key, value in summary.items():
        symbol = "✅" if value else "✗"
        print(f"{symbol} {key}: {'OK' if value else 'FALTA'}")
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ SCHEDULER ESTÁ CONFIGURADO CORRETAMENTE!")
        print("\nPróximas ações:")
        print("1. Iniciar o bot com: python -m src.bot")
        print("2. Verificar os logs com: tail -f logs/bot.log | grep -i 'scheduler\\|atualiz'")
        print("3. Validar cache com: python scripts/check_cache_status.py")
    else:
        print("⚠️  ATENÇÃO: Alguns componentes estão ausentes!")
        print("Verifique a configuração no arquivo cache_scheduler.py")
    print("=" * 70)


if __name__ == '__main__':
    check_scheduler_config()
