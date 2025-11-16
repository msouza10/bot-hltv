# 📊 Arquitetura de Cache - Bot HLTV

## Visão Geral

O bot agora utiliza um **sistema de cache em banco de dados** (libSQL) para armazenar partidas de CS2, reduzindo chamadas à API PandaScore e melhorando performance.

---

## 🏗️ Componentes Principais

### 1. **Cache Manager** (`src/database/cache_manager.py`)
Gerencia todas as operações de cache no banco de dados.

#### Métodos principais:
- **`cache_matches(matches, update_type)`** - Armazena/atualiza partidas no banco
  - Usa `INSERT ... ON CONFLICT` para upsert automático
  - Registra estatísticas de operação
  
- **`get_cached_matches(status, hours, limit)`** - Busca partidas do banco
  - Parâmetros:
    - `status`: "not_started" (próximas), "running" (ao vivo), "finished" (resultados)
    - `hours`: Últimas X horas (padrão 24h)
    - `limit`: Máximo de resultados (padrão 100)
  - Retorna lista de partidas parseadas do JSON

- **`get_cache_stats()`** - Estatísticas do cache
  - Total, ao vivo, próximas, finalizadas
  - Última atualização

- **`clean_old_cache(hours)`** - Remove partidas antigas
  - Remove partidas finalizadas há mais de X horas

---

### 2. **Cache Scheduler** (`src/services/cache_scheduler.py`)
Atualiza o cache periodicamente.

#### Ciclo de atualização:
- **A cada 5 minutos**: Atualiza partidas ao vivo (`update_live_matches`)
- **A cada 15 minutos**: Atualização completa (`update_all_matches`)
  - Busca: próximas, ao vivo, passadas (últimas 24h)
  - Armazena no banco
  - Agenda lembretes de notificação

---

### 3. **Fluxo de Dados**

```
PandaScore API
     ↓
Cache Scheduler (a cada 5-15 min)
     ↓
libSQL Bank (matches_cache table)
     ↓
Discord Commands (use o cache!)
```

---

## 🎯 Fluxo de Comandos (Agora com Cache)

### Comando: `/partidas`
```python
1. Busca do cache: status='not_started'
2. Se cache vazio → fallback para API
3. Retorna "próximas X partidas (cache atualizado)"
```

### Comando: `/aovivo`
```python
1. Busca do cache: status='running'
2. Se cache vazio → fallback para API
3. Retorna "X partida(s) ao vivo (cache atualizado)"
```

### Comando: `/resultados`
```python
1. Busca do cache: status='finished', últimas X horas
2. Se cache vazio → fallback para API
3. Retorna "últimos X resultado(s) (cache atualizado)"
```

---

## 📈 Benefícios

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Fonte de dados** | API a cada comando | Cache (1 req/5min) |
| **Latência** | ~1-2s por comando | <100ms (cache local) |
| **Rate limit API** | Alto (muitos comandos) | Baixo (5-15 min) |
| **Disponibilidade** | Depende da API | Funciona offline |
| **Custo** | Alto (muitas requisições) | Baixo (agendado) |

---

## 🔄 Fluxo de Notificações com Cache

Quando o cache é atualizado:

```
1. CacheScheduler busca partidas da API
2. Armazena no banco (update_matches)
3. Para cada servidor com notificações:
   - Agenda 5 lembretes por partida
   - Armazena em match_reminders
4. NotificationManager verifica a cada 1min
5. Envia lembretes automáticos no horário
```

---

## 📊 Dados Armazenados

### Tabela: `matches_cache`
```sql
- match_id (UNIQUE)
- match_data (JSON completo da API)
- status (not_started, running, finished)
- tournament_name
- begin_at, end_at (datas)
- updated_at (quando foi cacheado)
```

### Tabela: `match_reminders`
```sql
- guild_id (servidor Discord)
- match_id
- reminder_minutes_before (60, 30, 15, 5, 0)
- scheduled_time
- sent (boolean)
- sent_at (quando foi enviado)
```

---

## ⚡ Performance

### Sem Cache (Antes)
- Cada `/partidas` = 1 req API (~2s)
- 10 comandos/hora = 10 reqs API

### Com Cache (Depois)
- `/partidas` = 1 query banco (<100ms)
- 10 comandos/hora = 0 reqs API (já em cache!)
- Cache atualiza 5-15 min automaticamente

---

## 🛠️ Inicialização do Cache

O banco é inicializado automaticamente:

```bash
# Via init_db.py
python init_db.py

# Ou na primeira execução do bot
# O schema é criado no banco automaticamente
```

---

## 📝 Logs para Verificar

Procure por esses logs para confirmar que tudo está funcionando:

```
[INFO] ✓ CacheScheduler inicializado
[INFO] ✓ Agendador iniciado com Discord Tasks!
[INFO] ✓ Cache atualizado: X novas, Y atualizadas
[INFO] ✓ Lembretes agendados para partida Z
[INFO] ✓ Comando /partidas executado (X partidas do cache)
```

---

## 🔍 Debugging

### Verificar cache stats:
```sql
SELECT * FROM cache_stats;
```

### Ver partidas em cache:
```sql
SELECT match_id, status, begin_at FROM matches_cache ORDER BY begin_at;
```

### Ver lembretes pendentes:
```sql
SELECT * FROM match_reminders WHERE sent = 0 ORDER BY scheduled_time;
```

---

## ✅ Checklist de Funcionalidade

- [x] Cache Manager implementado
- [x] Partidas armazenadas no banco
- [x] Agendador atualiza cache a cada 5-15 min
- [x] Comandos `/partidas`, `/aovivo`, `/resultados` usam cache
- [x] Fallback para API se cache estiver vazio
- [x] Lembretes agendados automaticamente
- [x] NotificationManager verifica lembretes a cada 1 min
- [x] Banco é inicializado automaticamente
