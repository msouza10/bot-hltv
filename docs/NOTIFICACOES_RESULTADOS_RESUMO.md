# 🎯 Proposta: Notificações de Resultados de Partidas

## O que queremos?

Completar o **ciclo de vida** das notificações:
- ✅ Lembrete de início: "Começa em 1h", "Começa em 30min", etc
- ✅ Notificação ao vivo: (já feito apenas no cache)
- 🆕 **Notificação de resultado**: "Partida finalizada! Time A 2-1 Time B"

---

## 📊 Análise Rápida do Código

### ✅ O que JÁ EXISTE:

1. **Infraestrutura de lembretes** (`notification_manager.py`)
   - Loop que verifica a cada 1 minuto
   - Sistema de agendamento em banco de dados
   - Formatação com embeds

2. **Detecção de transições** (`cache_scheduler.py`)
   - Já detecta quando partida passa de RUNNING → FINISHED
   - Função: `check_running_to_finished_transitions()`

3. **Embeds de resultado** (`utils/embeds.py`)
   - `create_result_embed()` - Pronto e formatado
   - Mostra placar, mapas, torneio, etc

4. **Campo no BD**: `guild_config.notify_results`
   - Já existe para ativar/desativar

### ❌ O que FALTA:

1. **Tabela para agendar resultados**
   - Precisa rastrear quais resultados já foram notificados

2. **Métodos no NotificationManager**
   - `schedule_result_notification()` - Agendar resultado
   - `send_pending_result_notifications()` - Enviar pendentes

3. **Integração CacheScheduler ↔ NotificationManager**
   - Quando detecta fim de partida, agendar notificação

4. **Comando Discord** para ativar/desativar

---

## 💡 A Lógica Proposta

### Fluxo Simples (em 3 etapas)

#### 1️⃣ **Partida termina**
```
CacheScheduler detecta: running → finished
  └─ Chama: notification_manager.schedule_result_notification(guild_id, match_id)
     └─ Insere em novo banco: match_result_notifications
        └─ scheduled_time = AGORA (para envio rápido)
```

#### 2️⃣ **Loop verifica a cada 1 minuto**
```
NotificationManager._reminder_loop()
  ├─ Envia lembretes de INÍCIO (já faz)
  └─ ⭐ NOVO: Também envia notificações de RESULTADO
     └─ Busca match_result_notifications WHERE sent=0
     └─ Envia e marca como enviado (sent=1)
```

#### 3️⃣ **Resultado é enviado para Discord**
```
Por cada guild com notify_results=1:
  └─ Envia embed usando create_result_embed() que já existe
     └─ Mostra: "✅ Time A 2 - 1 Time B"
        (+ placar de mapas, torneio, etc)
```

---

## 📝 Modificações Necessárias

### 1. Banco de Dados
```sql
Adicionar tabela: match_result_notifications
  - guild_id
  - match_id
  - scheduled_time (quando enviar)
  - sent (se já foi enviado)
  - Índice em scheduled_time
```

### 2. NotificationManager
```python
+ schedule_result_notification(guild_id, match_id)
+ send_pending_result_notifications()
+ _send_result_notification(guild_id, match_id, match_data)

Modificar:
  _reminder_loop() → Chamar send_pending_result_notifications() também
```

### 3. CacheScheduler
```python
Modificar: check_running_to_finished_transitions()
  → Quando detectar transição, chamar schedule_result_notification()
    para cada guild com notify_results=1
```

### 4. Cog de Notificações
```python
+ Comando: /notificacoes-resultado on/off
  (similar ao comando /notificacoes existente)
```

---

## 🎯 Benefícios

| Item | Benefício |
|------|----------|
| **Reutiliza código** | Mesmo padrão de lembretes |
| **Rápido** | Notifica em <1 minuto após fim |
| **Evita duplicatas** | UNIQUE(guild_id, match_id) no BD |
| **Configurável** | Por guild (notify_results flag) |
| **Testado** | create_result_embed() já funciona |

---

## 📈 Timeline de Implementação

| Fase | Tarefa | Tempo Est. |
|------|--------|-----------|
| 1 | Adicionar tabela no schema | 10 min |
| 2 | 3 novos métodos em NotificationManager | 30 min |
| 3 | Integração em CacheScheduler | 15 min |
| 4 | Comando de ativação no Cog | 10 min |
| 5 | Testes | 15 min |
| **TOTAL** | | **~80 min** |

---

## ❓ FAQ Rápido

**P: E se a conexão falhar ao enviar?**
R: Loop de 1 min vai tentar novamente na próxima iteração.

**P: E se tiver muitos guilds?**
R: Não é problema. Um insert + algumas selects. ~1ms por guild.

**P: Funciona com partidas canceladas?**
R: Sim! `create_result_embed()` já trata status="canceled".

**P: Precisa de mais calls na API?**
R: Não. Usa dados do cache que já foi atualizado.

---

## ✅ Aprova a lógica?

Se sim, vamos implementar:
1. ✅ Schema do banco
2. ✅ NotificationManager
3. ✅ CacheScheduler
4. ✅ Cog de configuração
5. ✅ Testes
