# Proposta: Sistema de Notificações de Resultados

## 📋 Análise do Código Atual

### 1. **Estrutura Existente de Notificações**

#### NotificationManager (`notification_manager.py`)
- **Reminders para início**: Agendados para [60, 30, 15, 5, 0] minutos antes do início
- **Ciclo**: 
  1. `setup_reminders_for_match()` → Cria lembretes no banco
  2. `_reminder_loop()` → Roda a cada 1 minuto
  3. `send_pending_reminders()` → Verifica se é hora de enviar
  4. `_send_reminder_notification()` → Envia para o Discord

#### Cache Scheduler (`cache_scheduler.py`)
- **Atualiza cache a cada 15 min** (completo)
- **Atualiza partidas ao vivo a cada 5 min** (live matches)
- **Detecta transições de estado**:
  - `check_running_to_finished_transitions()` → Verifica se partidas passaram de RUNNING → FINISHED
  - `validate_state_transitions()` → Validação de transições em atualização completa

#### Banco de Dados (`schema.sql`)
- Tabela `match_reminders`: Rastreia lembretes de INÍCIO
  - `reminder_minutes_before`: Tempo antes do início
  - `sent`: Flag se foi enviado
  
- Tabela `notification_history`: Evita duplicatas
  - `notification_type`: 'upcoming', 'live', 'result'
  - UNIQUE(guild_id, match_id, notification_type)

- Tabela `guild_config`:
  - `notify_upcoming`: Notificações de próximas (padrão: 1)
  - `notify_live`: Notificações ao vivo (padrão: 1)
  - `notify_results`: Notificações de resultados (padrão: 0) ← **JÁ EXISTE!**

### 2. **O que Já Existe para Resultados**

✅ Campo `notify_results` na config (desativado por padrão)
✅ Campo `notification_type` suporta 'result'
✅ Função `create_result_embed()` em embeds.py (completa e formatada)
✅ Detecção de transições RUNNING→FINISHED acontecendo

### 3. **O que Falta**

❌ Sistema de agendamento de notificações de RESULTADOS (não usa `match_reminders`)
❌ Loop para enviar notificações de resultados
❌ Integração entre detecção de transições e envio de notificações

---

## 💡 Lógica Proposta

### Fluxo Completo de Notificações

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA DA PARTIDA                │
└─────────────────────────────────────────────────────────────┘

1️⃣  PARTIDA NÃO INICIADA (not_started)
    ├─ Agendador detecta nova partida
    ├─ NotificationManager.setup_reminders_for_match()
    │  └─ Cria 5 lembretes em match_reminders (60,30,15,5,0 min)
    └─ Loop de 1 min envia notificações "Começando em Xmin"
    
2️⃣  PARTIDA AO VIVO (running)
    ├─ Detectado pela atualização a cada 5 min
    └─ (Sem ação especial de notificação - só cache)
    
3️⃣  PARTIDA FINALIZADA (finished/canceled)
    ├─ Detectado por check_running_to_finished_transitions()
    ├─ Atualiza cache (status → finished)
    ├─ ⭐ NOVO: Agenda notificação de resultado imediatamente
    │  └─ Insere em nova tabela match_result_notifications
    │  └─ scheduled_time = NOW (para envio imediato)
    ├─ Loop de result notifications envia em <1 min
    │  └─ Recupera dados do cache com resultado
    │  └─ Cria embed com create_result_embed()
    │  └─ Envia para todos os guilds com notify_results=1
    └─ Marca como enviado em match_result_notifications

┌─────────────────────────────────────────────────────────────┐
│                    LOOPS DE VERIFICAÇÃO                     │
└─────────────────────────────────────────────────────────────┘

LOOP A CADA 15 MIN (CacheScheduler.update_all_matches)
├─ Atualiza cache com partidas próximas/ao vivo/finalizadas
├─ Detecta transições de estado
└─ Agenda resultados (se detectar finishing)

LOOP A CADA 5 MIN (CacheScheduler.update_live_matches)
├─ Atualiza apenas partidas ao vivo
├─ Detecta transições running→finished
└─ Agenda resultados (se detectar finishing) ⭐ MAIS RÁPIDO

LOOP A CADA 1 MIN (NotificationManager._reminder_loop) ⭐ NOVO
├─ Envia lembretes de INÍCIO (já existe)
└─ Envia notificações de RESULTADO (novo)
```

### Modificações Necessárias

#### 1️⃣ **Banco de Dados** (schema.sql)
```sql
-- Nova tabela para rastrear notificações de RESULTADO
CREATE TABLE IF NOT EXISTS match_result_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    scheduled_time DATETIME NOT NULL,  -- Quando enviar (quase sempre NOW)
    sent BOOLEAN DEFAULT 0,
    sent_at DATETIME,
    FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE,
    UNIQUE(guild_id, match_id)  -- Um resultado por partida por guild
);

CREATE INDEX IF NOT EXISTS idx_result_notif_scheduled 
    ON match_result_notifications(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_result_notif_sent 
    ON match_result_notifications(sent);
```

**Por que nova tabela?**
- `match_reminders` é para agendamento ANTECIPADO (vários horários)
- `match_result_notifications` é para agendamento REATIVO (quando partida termina)
- Separar evita conflitos de lógica e indexes

#### 2️⃣ **NotificationManager** (notification_manager.py)
Adicionar métodos:
```python
async def schedule_result_notification(self, guild_id: int, match_id: int) -> bool
    # Insere em match_result_notifications
    # scheduled_time = NOW para envio imediato
    # Reutiliza mesma filtragem de guild_config.notify_results

async def send_pending_result_notifications(self) -> int
    # Similar a send_pending_reminders()
    # Busca de match_result_notifications WHERE sent=0
    # Reutiliza _send_result_notification()

async def _send_result_notification(
    self, guild_id: int, match_id: int, match_data: str
) -> bool
    # Similar a _send_reminder_notification()
    # Usa create_result_embed() em vez de _create_reminder_embed()
```

Modificar método existente:
```python
async def _reminder_loop(self)
    # Continua enviando lembretes
    count_reminders = await self.send_pending_reminders()
    
    # ⭐ NOVO: Também envia resultados
    count_results = await self.send_pending_result_notifications()
```

#### 3️⃣ **CacheScheduler** (cache_scheduler.py)
Modificar método `check_running_to_finished_transitions()`:
```python
async def check_running_to_finished_transitions(self, running_matches):
    # Ao detectar transição running→finished:
    
    for transitioned_match in transitioned_matches:
        # 1. Atualizar cache (já faz)
        await self.cache_manager.cache_matches([transitioned_match], "live_transition")
        
        # ⭐ NOVO: Agendar resultado PARA TODOS os guilds
        if self.notification_manager:
            # Buscar todos os guilds com notify_results=1
            client = await self.cache_manager.get_client()
            result = await client.execute(
                "SELECT guild_id FROM guild_config WHERE notify_results = 1"
            )
            
            for row in result.rows:
                guild_id = row[0]
                # Agendar notificação de resultado
                await self.notification_manager.schedule_result_notification(
                    guild_id, 
                    transitioned_match.get('id')
                )
```

#### 4️⃣ **Cog de Notificações** (cogs/notifications.py)
Adicionar comando para ativar notificações de resultados:
```python
@nextcord.slash_command(
    name="notificacoes-resultado",
    description="Ativa/desativa notificações de RESULTADO de partidas"
)
async def notificacoes_resultado(
    self,
    interaction: nextcord.Interaction,
    ativar: bool = SlashOption(...)
):
    # Atualiza guild_config.notify_results
    # Similar ao comando /notificacoes existente
```

---

## 🎯 Resumo do Fluxo de Implementação

### Fase 1: Banco de Dados
- ✅ Adicionar tabela `match_result_notifications`

### Fase 2: NotificationManager
- ✅ `schedule_result_notification()` - Insere no banco
- ✅ `send_pending_result_notifications()` - Envia pendentes
- ✅ `_send_result_notification()` - Envia para Discord
- ✅ Modificar `_reminder_loop()` para chamar ambos

### Fase 3: CacheScheduler
- ✅ Modificar `check_running_to_finished_transitions()` para chamar `schedule_result_notification()`

### Fase 4: UI (Cog)
- ✅ Comando `/notificacoes-resultado` para toggle

### Fase 5: Testes
- ✅ Verificar ciclo completo de uma partida

---

## 📊 Exemplo de Execução

```
[13:00] Partida adicionada ao cache (status: not_started)
        → NotificationManager agenda 5 reminders (60,30,15,5,0 min)

[13:58] Reminder 60min: "Partida começando em 1 hora"
[14:28] Reminder 30min: "Partida começando em 30min"
...
[13:59] Reminder 0min: "🔴 PARTIDA COMEÇANDO AGORA!"

[14:00-14:45] Partida ao vivo (status: running)
              Loop de 5 min apenas atualiza cache

[14:46] Transição detectada: running → finished
        ├─ Cache atualizado com status=finished
        ├─ Resultado armazenado no match_data
        └─ ⭐ schedule_result_notification() inserido
            └─ scheduled_time = 14:46:00

[14:47] Loop de 1 min verifica resultados
        ├─ Encontra notificação com scheduled_time <= 14:47:00
        ├─ Envia: "✅ Time A 2 - 1 Time B"
        └─ Marca como enviado (sent=1)
```

---

## ✅ Vantagens desta Abordagem

1. **Reutiliza infraestrutura**: Mesmo padrão de lembretes
2. **Reativo**: Notifica assim que resultado fica disponível (<1 min)
3. **Evita duplicatas**: UNIQUE(guild_id, match_id) na tabela
4. **Configurável**: Toggle por guild (`notify_results`)
5. **Sem overhead**: Uma inserção + um lembrete = mínimo impacto
6. **Escalável**: Funciona mesmo com centenas de guilds

---

## ❓ Dúvidas Resolvidas

**P: Por que não reutilizar `match_reminders`?**
R: Porque tem padrão de "X minutos antes" que não faz sentido para resultados. Nova tabela é mais clara.

**P: Por que não enviar resultado direto em `check_running_to_finished_transitions`?**
R: Porque precisa tratar erro de timeout do Discord. Loop de 1 min garante retry automático.

**P: E se uma partida for cancelada?**
R: `create_result_embed()` já detecta `status="canceled"` e formata apropriadamente. Fluxo funciona igual.
