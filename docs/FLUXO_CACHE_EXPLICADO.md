# Fluxo de Cache e Informacoes - Esclarecimento

## 📊 Ciclo de Vida de Uma Partida na API PandaScore

```
ANTES DO INICIO              DURANTE                         DEPOIS
(Upcoming)                   (Running)                       (Finished/Canceled)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

status: not_started          status: running                 status: finished
begin_at: NULL               begin_at: 15:30                 begin_at: 15:30
end_at: NULL                 end_at: NULL                    end_at: 17:00
scheduled_at: 20:00          scheduled_at: 20:00             scheduled_at: 20:00
results: []                  results: [1, 0]                 results: [2, 0]
games: []                    games: [mapa1...]              games: [mapa1, mapa2]
```

---

## ✅ Resposta à Sua Dúvida

**Pergunta**: "Isso precisa estar no cache tanto de renew tanto nesse de inicio?"

**Resposta**: **NÃO, não precisa fazer nada especial!** 

### Por Quê?

A **API PandaScore já retorna TUDO** que você precisa em uma ÚNICA chamada:

```json
{
  "id": 1269341,
  "status": "finished",
  "begin_at": "2025-11-16T15:30:00Z",  ← ISSO JÁ VEM DA API!
  "end_at": "2025-11-16T17:00:00Z",    ← ISSO JÁ VEM DA API!
  "results": [2, 0],                   ← ISSO JÁ VEM DA API!
  "games": [                           ← ISSO JÁ VEM DA API!
    { "teams": [{"score": 16}, {"score": 10}] },
    { "teams": [{"score": 16}, {"score": 12}] }
  ]
}
```

---

## 🔄 Como Funciona Atualmente (Correto)

### 1. **Cache Scheduler** - a cada 5-15 minutos
```python
# Busca TUDO da API em uma única chamada
past_matches = await api_client.get_past_matches(hours=24, per_page=20)

# Cada partida vem COM begin_at, end_at, results, games
# Salva TUDO no banco de dados
await cache_manager.cache_matches(past_matches, "all")
```

### 2. **Database** - libSQL
```sql
-- Tabela matches_cache
id | match_id | match_data (JSON)         | status    | updated_at
---+----------+------------------------+----------+------------
1  | 1269341  | {begin_at, end_at, ...}| finished | 2025-11-16
2  | 1269340  | {begin_at, end_at, ...}| canceled | 2025-11-16
```

### 3. **Memory Cache** - quando busca
```python
# Lê direto do banco de dados
SELECT match_data FROM matches_cache
WHERE status IN ('finished', 'canceled', 'postponed')

# Cada match_data já tem TUDO:
# {
#   "begin_at": "2025-11-16T15:30:00Z",
#   "end_at": "2025-11-16T17:00:00Z",
#   "results": [2, 0],
#   "games": [...]
# }

# Coloca em memória e retorna
_memory_cache["finished"] = [match1, match2, ...]
```

### 4. **Comando /resultados** - busca do cache
```python
# Tier 1: Memory cache (< 100ms)
matches = await cache_manager.get_cached_matches_fast("finished", 5)

# Match já tem TUDO que precisa:
for match in matches:
    embed = create_result_embed(match)
    # Usa:
    #   - match['begin_at']
    #   - match['end_at']
    #   - match['results']
    #   - match['games']
    #   - match['status']
```

---

## 🎯 Fluxo de Dados - Diagrama

```
┌─────────────────────────────────────────────────────────────┐
│ API PandaScore (5-15 min)                                   │
│ GET /csgo/matches/past?hours=24                            │
│                                                             │
│ Retorna:                                                    │
│ [{                                                          │
│   id: 1269341,                                              │
│   status: "finished",                                       │
│   begin_at: "2025-11-16T15:30Z",  ← CRITICA!             │
│   end_at: "2025-11-16T17:00Z",    ← CRITICA!             │
│   results: [2, 0],                ← CRITICA!             │
│   games: [...],                   ← CRITICA!             │
│   ...outros campos                                         │
│ }]                                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Cache Manager (cache_matches)                               │
│ Salva TUDO no banco (match_data = JSON serializado)        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Database (libSQL) - matches_cache                           │
│ match_data: '{"begin_at": "...", "end_at": "...", ...}'   │
│                                                             │
│ Dados PRESERVADOS exatamente como vieram da API            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Memory Cache (_memory_cache["finished"])                    │
│ Carrega JSON do banco e deserializa                         │
│ Tem acesso COMPLETO a begin_at, end_at, results, games    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Comando /resultados                                         │
│ create_result_embed(match)                                  │
│                                                             │
│ Usa todos os campos:                                        │
│ - match['begin_at'] → calcula duração                      │
│ - match['end_at'] → mostra quando finalizou               │
│ - match['results'] → mostra placar final                  │
│ - match['games'] → mostra scores dos mapas               │
│ - match['status'] → ativa lógica cancelado/finalizado    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 O Que Está Sendo Salvo (Completo)

Quando a API retorna uma partida passada:

```python
match_data = {
    "id": 1269341,
    "status": "finished",
    "scheduled_at": "2025-11-16T15:00:00Z",
    "begin_at": "2025-11-16T15:00:00Z",      # ✅ SALVO
    "end_at": "2025-11-16T16:30:00Z",        # ✅ SALVO
    "opponents": [
        {"opponent": {"id": 123, "name": "SPARTA"}},
        {"opponent": {"id": 124, "name": "Nuclear TigeRES"}}
    ],
    "results": [
        {"team_id": 124, "score": 2},         # ✅ SALVO
        {"team_id": 123, "score": 0}
    ],
    "games": [                                # ✅ SALVO
        {
            "position": 1,
            "state": "finished",
            "teams": [
                {"id": 124, "score": 16},
                {"id": 123, "score": 10}
            ]
        },
        {
            "position": 2,
            "state": "finished",
            "teams": [
                {"id": 124, "score": 16},
                {"id": 123, "score": 12}
            ]
        }
    ],
    "league": {...},
    "tournament": {...},
    "number_of_games": 3,
    # ... TUDO MAIS VINDO DA API
}
```

**Tudo isso é convertido para JSON e gravado em `matches_cache.match_data`**

---

## ✅ Ciclo Completo Funcionando

```
PRIMEIRA EXECUCAO (00:27)
├─ API retorna 20 partidas passadas (COM begin_at, end_at, results, games)
├─ Cache Manager salva TUDO no banco
├─ Memory Cache pula (primeira vez, vazio)
└─ Stats: "20 partidas passadas obtidas"

USUARIO EXECUTA /resultados (00:27:49)
├─ Tier 1: Memory cache vazio (ainda nao foi preenchido)
├─ Tier 2: Busca do banco (encontra 20 partidas)
│         ├─ Toma a coluna match_data (JSON completo)
│         ├─ Deserializa e tem access a begin_at, end_at, results, games
│         └─ Retorna 5 melhores
├─ Cria embed com create_result_embed(match)
│         ├─ Acessa match['begin_at']
│         ├─ Acessa match['end_at']
│         ├─ Acessa match['results']
│         └─ Acessa match['games']
└─ Envia para Discord

PROXIMA EXECUCAO DO SCHEDULER (próximas 15 min)
├─ Atualiza cache (mesmo 20 partidas, nada novo)
├─ Chama _update_memory_cache()
├─ Memory cache agora carregado
└─ Próxima vez que /resultados for executado
   └─ Tier 1: Memory cache (< 100ms) retorna dados

PROXIMA EXECUCAO DE /resultados
├─ Tier 1: Memory cache JÁ PREENCHIDO
├─ Retorna 5 do memory cache em < 100ms
├─ Cria embed (mesmos dados, mesma qualidade)
└─ Envia para Discord
```

---

## 🎯 Resumo

| Pergunta | Resposta |
|----------|----------|
| **Precisa guardar begin_at, end_at, results, games especialmente?** | NÃO - API já fornece tudo |
| **Precisa fazer algo especial no "renew" ou "inicio"?** | NÃO - cache é automático |
| **Onde esses dados estão guardados?** | Em `matches_cache.match_data` (JSON) |
| **Como são acessados?** | Deserializados quando lidos do DB |
| **Memory cache tem acesso a isso tudo?** | SIM - deserializa na leitura |
| **O embed consegue acessar begin_at, end_at?** | SIM - estão no objeto match |

---

## ✅ Conclusão

**Está tudo funcionando corretamente!**

- ✅ API retorna dados completos
- ✅ Cache Manager salva TUDO
- ✅ Banco armazena JSON completo
- ✅ Memory cache deserializa corretamente
- ✅ Embed usa todos os campos necessários
- ✅ Nenhuma informação é perdida

**Não precisa fazer nada especial!** O sistema já está capturando e armazenando todas as informações necessárias automaticamente. 🚀

---

_Esclarecimento: 16/11/2025_
