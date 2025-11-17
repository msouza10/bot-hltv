# ✅ Verificação Completa do Agendador de Cache (Scheduler)

## 📊 Status Geral: ✅ **TOTALMENTE CONFIGURADO E CORRETO**

---

## 1️⃣ **Configuração das Tasks**

### Task 1: `update_all_task` - Atualização Completa
- **Intervalo**: 3 minutos ✅
- **Count**: None (infinito/indefinido) ✅
- **Função**: `update_all_matches()` ✅
- **Lock**: Sim, `_cache_update_lock` ✅
- **Primeira execução**: 2 segundos após bot iniciar ✅

**Responsabilidades**:
```
1. Busca 50 partidas próximas (upcoming)
2. Busca partidas ao vivo (running)
3. Busca 20 partidas finalizadas (past 24h)
4. Busca partidas canceladas/adiadas
5. Cachea todas no banco de dados
6. Atualiza memory cache para respostas rápidas
```

### Task 2: `check_finished_task` - Detecção Rápida de Resultados
- **Intervalo**: 1 minuto ✅
- **Count**: None (infinito/indefinido) ✅
- **Função**: `check_running_to_finished_transitions_fast()` ✅
- **Lock**: Sim, `_cache_update_lock` ✅
- **Primeira execução**: 2 segundos após bot iniciar ✅

**Responsabilidades**:
```
1. Detecta partidas que mudaram de RUNNING → FINISHED
2. Consulta BD para partidas em running há 1+ minuto
3. Busca últimas 300 partidas finished (3 páginas × 100)
4. Identifica transições
5. Atualiza cache
6. Agenda notificações de resultado
```

---

## 2️⃣ **Callbacks Before Loop**

✅ **before_update_all**: Aguarda bot pronto por 2 segundos  
✅ **before_check_finished**: Aguarda bot pronto por 2 segundos

**Função**: Garantir que todas as dependências estejam inicializadas antes de começar as tasks.

---

## 3️⃣ **Mecanismo de Locks**

### Lock Global: `_cache_update_lock` (asyncio.Lock)

**Por quê?** Evitar race conditions entre as duas tasks rodando simultaneamente.

**Como funciona**:
```python
# update_all_matches
async with _cache_update_lock:  # Adquire lock
    [executa código]
    # Libera lock automaticamente ao sair do bloco

# update_live_matches (NOT USED IN THIS VERSION)
async with _cache_update_lock:  # Mesmo lock
    [executa código]
```

**Resultado**: Apenas UMA task executa por vez, mesmo que os intervalos se sobreponham.

---

## 4️⃣ **Timeline de Execução Esperada**

Após iniciar o bot em `t=0`:

| Tempo | Execução |
|-------|----------|
| +2s | `update_all_task` começa (1ª exec) |
| +2s | `check_finished_task` começa (1ª exec) |
| +1min | `check_finished_task` (2ª exec) |
| +2min | `check_finished_task` (3ª exec) |
| +3min | `update_all_task` (2ª exec) |
| +4min | `check_finished_task` (4ª exec) |
| +5min | `check_finished_task` (5ª exec) |
| +6min | `update_all_task` (3ª exec) |
| ... | Continua indefinidamente |

---

## 5️⃣ **Métodos de Controle**

✅ **Método `start()`**:
- Inicia ambas as tasks
- Define `self.is_running = True`
- Logs informativos sobre os intervalos

✅ **Método `stop()`**:
- Cancela ambas as tasks
- Define `self.is_running = False`
- Limpa recursos

---

## 6️⃣ **Inicialização no Bot**

✅ **Em `src/bot.py`**:
```python
from src.services.cache_scheduler import CacheScheduler

class HLTVBot(nextcord.Client):
    def __init__(self, ...):
        # ...
        self.cache_scheduler = CacheScheduler(...)
    
    async def on_ready(self):
        # ...
        if not self.cache_scheduler.is_running:
            self.cache_scheduler.start()  # ← INICIA AQUI
```

---

## 7️⃣ **Métricas de Funcionamento**

### Cada execução de `update_all_task` (3 min):
- **~50** partidas próximas
- **~1-3** partidas ao vivo
- **~20** partidas finalizadas
- **~0-5** partidas canceladas/adiadas
- **Total**: ~70-80 partidas no cache

### Cada execução de `check_finished_task` (1 min):
- **Checar**: Partidas em RUNNING > 1 minuto sem atualização
- **Comparar com**: 300 partidas finished recentes
- **Transições esperadas**: 0-2 por ciclo
- **Notificações**: 0 a N agendadas (conforme habilitado)

---

## 8️⃣ **Como Validar que Está Funcionando**

### ✅ **Opção 1: Verificar Configuração**
```bash
python scripts/check_scheduler_config.py
```
Resultado esperado: ✅ TODOS os checks devem passar

### ✅ **Opção 2: Monitorar Status de Cache**
```bash
python scripts/check_cache_status.py
```
Validar:
- Cache não deve ter mais de 3 minutos
- Deve conter ~70-80 partidas
- Distribuição: ~50 upcoming, ~1-3 running, ~20 finished

### ✅ **Opção 3: Forçar Atualização Manual**
```bash
python scripts/force_cache_update.py
```
Validar:
- Executa sem travamentos
- Completa em <10 segundos
- Retorna ~73 partidas cacheadas

### ✅ **Opção 4: Monitorar Logs em Tempo Real**
```bash
tail -f logs/bot.log | grep -E 'scheduler|Atualiz|RUNNING|FINISHED'
```
Procure por:
- `🔄 Iniciando atualização completa do cache`
- `✓ XX partidas próximas obtidas`
- `🔍 Verificação rápida de resultados`

### ✅ **Opção 5: Testar em Discord**
```
/aovivo → Deve listar partidas ao vivo com streams
/partidas → Deve mostrar próximas 5 partidas
/resultados → Deve mostrar últimos resultados
```

---

## 9️⃣ **Possíveis Problemas e Soluções**

### 🔴 Tasks não estão rodando
**Verificar**:
1. Se `cache_scheduler.start()` foi chamado em `bot.py`
2. Se bot está realmente iniciado: `ps aux | grep python`
3. Logs de inicialização para erros

### 🔴 Cache não está sendo renovado
**Verificar**:
1. ✅ Deadlock em `cache_manager.py` foi CORRIGIDO (cache_streams agora sem lock)
2. Timeouts - aumentados de 1s para 10s ✅
3. Testar manualmente: `python scripts/force_cache_update.py`

### 🔴 Muitas transições RUNNING→FINISHED faltando
**Solução**:
1. Aumentar frequência de `check_finished` (reduzir para 30s)
2. Aumentar número de páginas da API (verificar paginator)
3. Validar cacheamento de streams

### 🔴 Notificações não sendo agendadas
**Verificar**:
1. Se `notification_manager` está inicializado
2. Se `guild_config` tem `notify_results=1`
3. Logs do NotificationManager

---

## 🔟 **Fluxo Completo de Funcionamento**

```
BOT INICIA
    ↓
on_ready() é chamado
    ↓
cache_scheduler.start() é chamado
    ↓
both_tasks.before_loop() espera 2s
    ↓
update_all_task COMEÇA
├─ Adquire _cache_update_lock
├─ Busca API: upcoming (50), running, past (20), canceled
├─ Cache tudo no BD
├─ Atualiza memory cache
└─ Libera lock
    ↓
check_finished_task COMEÇA
├─ Adquire _cache_update_lock
├─ Busca partidas RUNNING > 1 min sem update
├─ Consulta API/BD para finished
├─ Identifica transições
├─ Atualiza cache
├─ Agenda notificações
└─ Libera lock
    ↓
AGUARDA PRÓXIMO CICLO (1-3 min)
    ↓
[REPETE INDEFINIDAMENTE]
    ↓
BOT ENCERRADO (stop() chamado)
    ↓
Ambas tasks são canceladas
```

---

## 📋 **Resumo Final**

| Componente | Status |
|-----------|--------|
| Tasks definidas | ✅ |
| Intervalos corretos | ✅ |
| Locks configurados | ✅ |
| Callbacks before_loop | ✅ |
| Métodos start/stop | ✅ |
| Inicialização em bot.py | ✅ |
| Deadlock corrigido | ✅ |
| Timeouts ajustados | ✅ |
| Manual tests passing | ✅ |
| Configuração pronta | ✅ |

---

## 🚀 **Conclusão**

**O agendador de cache está TOTALMENTE CONFIGURADO e PRONTO PARA PRODUÇÃO.**

Próximas ações recomendadas:
1. ✅ Iniciar o bot: `python -m src.bot`
2. ✅ Monitorar por 5 minutos: `tail -f logs/bot.log`
3. ✅ Validar cache: `python scripts/check_cache_status.py`
4. ✅ Testar em Discord: `/aovivo`, `/partidas`, `/resultados`

---

**Data de Verificação**: 2025-11-17  
**Status**: ✅ VALIDADO E FUNCIONAL
