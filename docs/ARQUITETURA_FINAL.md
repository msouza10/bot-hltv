# 🏗️ Arquitetura Final do Fluxo de Dados

## 📥 Entrada: API PandaScore

```
┌─────────────────────────────────────────┐
│     PandaScore API (CS2 Matches)        │
├─────────────────────────────────────────┤
│ GET /csgo/matches/upcoming              │
│ GET /csgo/matches/running               │
│ GET /csgo/matches/past?filter=finished  │ ← NOVO
│ GET /csgo/matches/past?filter=canceled  │ ← NOVO
└─────────────────────────────────────────┘
                    ↓
```

## 🔄 Processamento

```
┌──────────────────────────────────────────────────────┐
│         pandascore_service.py                        │
├──────────────────────────────────────────────────────┤
│ • get_upcoming_matches(50)                           │
│ • get_running_matches()                              │
│ • get_past_matches() + filter[status]=finished       │
│ • get_canceled_matches() + filter[status]=canceled   │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│         cache_scheduler.py                           │
├──────────────────────────────────────────────────────┤
│ update_all_matches():                                │
│ ├─ Busca 50 futuras + 2 ao vivo + 20 finalizadas    │
│ └─ + 20 canceladas/adiadas                          │
│                                                      │
│ update_live_matches():                               │
│ └─ Busca apenas ao vivo (a cada 5 min)              │
└──────────────────────────────────────────────────────┘
                    ↓
```

## 💾 Armazenamento

```
┌──────────────────────────────────────────────────────┐
│              cache_manager.py                        │
├──────────────────────────────────────────────────────┤
│ INSERT/UPDATE: matches_cache                         │
│ ├─ match_id (UNIQUE)                                │
│ ├─ match_data (JSON com TUDO)                       │
│ ├─ status (not_started, running, finished, etc)     │
│ ├─ tournament_name                                  │
│ ├─ begin_at (data real)                             │
│ ├─ end_at (data real ou NULL)                       │
│ └─ cached_at, updated_at                            │
│                                                      │
│ CACHE HIERARQUIZADO:                                 │
│ ├─ Memory: < 100ms (92 partidas)                    │
│ ├─ Database: < 3s (com timeout)                     │
│ └─ API: Fallback (se cache falhar)                  │
└──────────────────────────────────────────────────────┘
                    ↓
```

## 🎨 Exibição

```
┌──────────────────────────────────────────────────────┐
│              embeds.py                               │
├──────────────────────────────────────────────────────┤
│ create_match_embed():                                │
│ ├─ Status: not_started / running                    │
│ ├─ Mostra: times, horário, torneio, formato         │
│ └─ Extras: versão, tipo, remarcada                  │
│                                                      │
│ create_result_embed():                               │
│ ├─ Status: finished / canceled / postponed          │
│ ├─ Mostra: placar, mapas, duração                   │
│ ├─ NOVO: nomes dos mapas                            │
│ ├─ NOVO: forfeit detection                          │
│ ├─ NOVO: empate detection                           │
│ ├─ NOVO: versão do jogo                             │
│ ├─ NOVO: tipo de partida                            │
│ ├─ NOVO: indicador de remarcada                     │
│ └─ NOVO: timestamp real no footer                   │
└──────────────────────────────────────────────────────┘
                    ↓
```

## 📤 Discord

```
┌──────────────────────────────────────────────────────┐
│              Discord Bot                             │
├──────────────────────────────────────────────────────┤
│ /partidas [quantidade]                               │
│ └─ Mostra embed create_match_embed()                │
│                                                      │
│ /aovivo                                              │
│ └─ Mostra embed create_match_embed()                │
│                                                      │
│ /resultados [horas] [quantidade]                    │
│ └─ Mostra embed create_result_embed()               │
│                                                      │
│ Notificações automáticas:                            │
│ ├─ 60 min antes: "match starts in 1h"               │
│ ├─ 30 min antes: "match starts soon"                │
│ ├─ 15 min antes: "5 min to start"                   │
│ ├─ 5 min antes: "LIVE IN 5 MIN!"                    │
│ └─ Ao vivo: "LIVE NOW!"                             │
└──────────────────────────────────────────────────────┘
```

---

## 🔍 Identificação de Status (CORE LOGIC)

```python
# ÚNICA VERDADE DE NEGÓCIO: O CAMPO "status"

match_data = {...}
status = match_data["status"]  # ← TUDO QUE VOCÊ PRECISA

# Todos os campos abaixo são OPCIONAIS para lógica
# (apenas para exibição e contexto):

begin_at = match_data.get("begin_at")      # Quando começou
end_at = match_data.get("end_at")          # Quando terminou (pode ser None)
results = match_data.get("results", [])    # Placar
games = match_data.get("games", [])        # Mapas

# O status NUNCA ERRA - ele é a fonte de verdade!
```

---

## 📊 Dados Capturados por Status

### NOT_STARTED
```
✅ Horário marcado (scheduled_at)
✅ Times (opponents[0,1])
✅ Torneio (tournament, league, serie)
✅ Formato (number_of_games = BO3)
✅ Versão do jogo
✅ Tipo de partida
```

### RUNNING
```
✅ Todas do NOT_STARTED
✅ Placar parcial (results)
✅ Mapas em progresso (games)
✅ Início real (begin_at)
```

### FINISHED
```
✅ Todas do RUNNING
✅ Placar final (results com scores > 0)
✅ Nomes dos mapas (games[].map.name) ← NOVO
✅ Scores por mapa (games[].teams[].score)
✅ Forfeit flag ← NOVO
✅ Draw flag ← NOVO
✅ Match type ← NOVO
✅ Timestamp no footer ← NOVO
```

### CANCELED
```
✅ Times (opponents)
✅ Torneio planejado
✅ Formato planejado
✅ Motivo (cancellation_reason se houver)
✅ Emoji ❌ especial
```

---

## 🎯 Performance

```
Hierarquia de Cache:

1. Memory Cache (92 matches)
   └─ < 100ms ✅

2. Database Cache
   └─ < 3s ✅ (com timeout)
   
3. API (PandaScore)
   └─ Backup se cache falhar
```

**Resultado:** Discord interactions sempre < 3s ✅

---

## 📈 Estatísticas

```
API Calls por Ciclo (15 min):
├─ 50 partidas futuras
├─ 2 partidas ao vivo
├─ 20 partidas finalizadas ← NOVO
└─ 20 partidas canceladas ← NOVO
   = 92 total no cache

Total de Informações Capturadas:
├─ Status (5 possíveis)
├─ Placar + detalhes de mapas
├─ Nomes dos mapas
├─ Versão do jogo
├─ Tipo de partida
├─ Forfeit/Draw/Rescheduled
└─ Timestamps reais
   = ~40 campos por partida
```

---

## 🚀 Deployment

```
Bot Status: ✅ LIVE

Services Running:
├─ Discord Bot: Connected ✅
├─ Cache Scheduler: Active (15min) ✅
├─ Live Updater: Active (5min) ✅
├─ Notification Manager: Active ✅
└─ Database: Synced ✅

Ready for:
✅ User commands (/partidas, /aovivo, /resultados)
✅ Automatic notifications (5 lembretes per match)
✅ Real-time updates (live matches)
✅ Historical data (past matches)
```

---

## 🔐 Data Flow Security

```
API ──(JSON)──> Validation ──(Parsed)──> Cache ──(Display)──> Embed ──> Discord

✅ Cada etapa valida dados
✅ Timeout protege contra hang
✅ Error handling em cascata
✅ Fallback para dados cacheados
```

**Resultado:** Nunca mais 404 Unknown Interaction! 🎉
