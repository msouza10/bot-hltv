# Análise Completa da Estrutura de Retorno da API PandaScore

**Data**: 17 de Novembro de 2025  
**Status**: Produção  
**Documento**: Referência para desenvolvimento

---

## 📋 Sumário Executivo

A API do PandaScore retorna dados de partidas CS2 com estrutura hierárquica complexa. Este documento mapeia TODOS os campos, suas variações por status de match, e como usá-los corretamente.

**Três variações principais por status**:
1. **UPCOMING** (not_started): Matches futuros, `begin_at` confirmado
2. **RUNNING**: Matches em progresso, games parcialmente concluídos
3. **FINISHED/CANCELED**: Matches completados, dados históricos completos

---

## 🎯 Estrutura Top-Level do Match

### Campo: Status HTTP
```
Status: 200
Timeout: 10s (recomendado)
```

### Campo: Headers Críticos (Rate Limiting & Paginação)
```json
{
  "X-Rate-Limit-Remaining": "889",     // Requisições restantes/hora
  "X-Rate-Limit-Used": "111",          // Requisições usadas/hora
  "X-Total": "288",                    // Total de matches naquele endpoint
  "X-Page": "1",                       // Página atual (começa em 1)
  "X-Per-Page": "10",                  // Items por página (max 50)
  "Link": "<...?page=2>; rel=\"next\"" // Link para próxima página
}
```

**⚠️ CRÍTICO**: Sempre checar `X-Rate-Limit-Remaining`. Se < 50, esperar 1 hora antes de nova chamada.

---

## 📊 Estrutura Principal do Match (Top Level)

### Match Object - Campos SEMPRE Presentes

```json
{
  "id": 1269173,                    // PK: Match ID único
  "name": "Upper bracket quarterfinal 2: ALLIN vs WSG",
  "slug": "allinners-vs-washington-2025-11-17",
  "status": "not_started",          // not_started | running | finished | canceled
  "match_type": "best_of",          // Sempre "best_of" para CS2
  "number_of_games": 3,            // Sempre 3 para CS2 (BO3)
  "draw": false,                   // Raramente true
  "forfeit": false,                // true se alguém não apareceu
  "rescheduled": false,            // true se foi remarcado
  "detailed_stats": false,         // true = dados mais detalhados disponíveis
  "winner_type": "Team",           // Sempre "Team" para matches
  
  // Identificadores de contexto
  "league_id": 5232,               // Liga que organiza
  "tournament_id": 18006,          // Torneio/evento
  "serie_id": 9863,                // Série dentro do torneio
  
  // Campos temporais (VARIAM por status)
  "begin_at": "2025-11-17T15:30:00Z",           // Hora inicial (null se canceled)
  "end_at": null,                               // Hora final (null se não terminado)
  "scheduled_at": "2025-11-17T15:30:00Z",      // Hora planejada
  "original_scheduled_at": "2025-11-17T15:30:00Z", // Hora original (se remarcado)
  
  // Resultado
  "winner": null,                  // null até não_started | {id, name, ...} se finished
  "winner_id": null,               // null até finished
  
  // Metadados
  "modified_at": "2025-11-17T17:57:28Z",
  "game_advantage": null,
  "videogame_version": null
}
```

---

## 🕐 Campos Temporais - Variações por Status

### UPCOMING (not_started)
```json
{
  "begin_at": "2025-11-17T15:30:00Z",  // ✅ SEMPRE PREENCHIDO
  "end_at": null,                      // ✅ null
  "scheduled_at": "2025-11-17T15:30:00Z", // ✅ Igual a begin_at
  "original_scheduled_at": "2025-11-17T15:30:00Z" // ✅ Igual a begin_at (a menos que remarcado)
}
```

### RUNNING
```json
{
  "begin_at": "2025-11-17T18:02:01Z",  // ✅ Hora real de início
  "end_at": null,                      // ✅ null (ainda em progresso)
  "scheduled_at": "2025-11-17T18:00:00Z", // ✅ Hora planejada original
  "original_scheduled_at": "2025-11-17T18:00:00Z" // ✅ Hora original
}
```

### FINISHED/CANCELED
```json
{
  "begin_at": null,                    // ❌ null (dados históricos)
  "end_at": null,                      // ❌ null (API não fornece)
  "scheduled_at": null,                // ❌ null (não relevante)
  "original_scheduled_at": null        // ❌ null (não relevante)
}
```

**🔴 ATENÇÃO**: Matches FINISHED/CANCELED **NÃO têm begin_at**! Usar `results` e `games[].end_at` para contexto temporal.

---

## 👥 Dados dos Times (Opponents)

### Estrutura Opponents
```json
{
  "opponents": [
    {
      "type": "Team",
      "opponent": {
        "id": 135092,
        "name": "ALLINNERS",
        "acronym": "ALLIN",
        "location": "KZ",           // País (ISO 3166-1 alpha-2)
        "slug": "allinners",
        "image_url": "https://cdn.pandascore.co/images/team/...",
        "dark_mode_image_url": "https://cdn.pandascore.co/dark_images/team/...",
        "modified_at": "2025-11-10T15:35:04Z"
      }
    },
    {
      "type": "Team",
      "opponent": {
        "id": 137476,
        "name": "Washington",
        "acronym": "WSG",
        "location": "",  // ⚠️ Pode ser vazio!
        "slug": "washington-cs-go",
        "image_url": "https://cdn.pandascore.co/images/team/...",
        "dark_mode_image_url": null,  // ⚠️ Pode ser null!
        "modified_at": "2025-11-16T08:06:52Z"
      }
    }
  ]
}
```

**Alternativas de acesso** (para compatibilidade):
- Usar `opponents[0].opponent` para time 1
- Usar `opponents[1].opponent` para time 2
- Campo `results` também tem: `results[0].team_id` (match com opponents pela order)

---

## 🎮 Dados dos Games (Partidas Individuais)

### Estrutura Games - Variações por Status Match

#### UPCOMING (games not_started)
```json
{
  "games": [
    {
      "id": 194264,
      "position": 1,              // 1, 2, ou 3 (BO3)
      "status": "not_started",    // ✅ Todos not_started
      "complete": false,          // ✅ false
      "finished": false,          // ✅ false
      "match_id": 1269173,        // FK → match.id
      
      "begin_at": null,           // ✅ null
      "end_at": null,             // ✅ null
      "length": null,             // ✅ null
      
      "forfeit": false,
      "detailed_stats": false,
      
      "winner": {
        "id": null,               // ✅ null
        "type": "Team"
      },
      "winner_type": "Team"
    },
    // ... games 2 e 3
  ]
}
```

#### RUNNING (games misto)
```json
{
  "games": [
    {
      "id": 189717,
      "position": 1,
      "status": "finished",       // ✅ Pode ser finished
      "complete": true,          // ✅ true
      "finished": true,          // ✅ true
      "match_id": 1253023,
      
      "begin_at": "2025-11-17T18:02:01Z",  // ✅ Preenchido
      "end_at": "2025-11-17T18:43:02Z",    // ✅ Preenchido (pode ser null se still running)
      "length": 2460,            // ✅ Segundos (pode ser null)
      
      "forfeit": false,
      "detailed_stats": false,
      
      "winner": {
        "id": 127829,             // ✅ ID do time vencedor
        "type": "Team"
      },
      "winner_type": "Team"
    },
    {
      "id": 189719,
      "position": 3,
      "status": "running",        // ✅ Game atual em progresso
      "complete": false,         // ✅ false
      "finished": false,         // ✅ false
      "match_id": 1253023,
      
      "begin_at": "2025-11-17T19:46:22Z",
      "end_at": null,            // ✅ Ainda rodando
      "length": null,
      
      "forfeit": false,
      "winner": {
        "id": null,              // ✅ Ainda não tem vencedor
        "type": "Team"
      }
    }
  ]
}
```

#### FINISHED (games all finished)
```json
{
  "games": [
    {
      "id": 176592,
      "position": 1,
      "status": "finished",       // ✅ Todos finished
      "complete": true,          // ✅ Todos true
      "finished": true,          // ✅ Todos true
      "match_id": 1200600,
      
      "begin_at": null,          // ⚠️ Pode ser null
      "end_at": null,            // ⚠️ Pode ser null (mesmo se finished!)
      "length": null,            // ⚠️ Pode ser null
      
      "forfeit": true,           // ⚠️ Pode ser true
      "winner": {
        "id": 135505,
        "type": "Team"
      }
    }
  ]
}
```

**Regras de Lógica**:
- Se `games[i].status == "finished"` → game tem resultado
- Se `games[i].forfeit == true` → vitória não-competitiva
- Se `games[i].end_at == null` → dados incompletos (pode estar em live ou API não retorna)
- Usar `games[i].length` para duração (em segundos)

---

## 🏆 Dados de Contexto (League, Serie, Tournament)

### League Object
```json
{
  "league": {
    "id": 5232,
    "name": "CCT Europe",
    "slug": "cs-go-cct-europe",
    "url": null,
    "image_url": "https://cdn.pandascore.co/images/league/...",
    "modified_at": "2024-04-13T08:58:18Z"
  }
}
```

### Serie Object (Temporada/Série)
```json
{
  "serie": {
    "id": 9863,
    "name": "European Contenders #2",
    "year": 2025,
    "season": "3",
    "begin_at": "2025-11-10T15:30:00Z",
    "end_at": "2025-11-24T21:30:00Z",
    "winner_id": null,
    "winner_type": "Team",
    "slug": "cs-go-cct-europe-european-contenders-2-3-2025",
    "full_name": "European Contenders #2 season 3 2025",
    "league_id": 5232,
    "modified_at": "2025-11-10T15:20:46Z"
  }
}
```

### Tournament Object (Evento/Etapa)
```json
{
  "tournament": {
    "id": 18006,
    "name": "Playoffs",
    "type": "online",                 // online | offline | online-and-offline
    "country": null,                  // null se online
    "region": "EEU",                  // EEU | WEU | OCE | SA | etc
    "tier": "d",                      // d | c | b | a | s (tier do torneio)
    "begin_at": "2025-11-10T15:30:00Z",
    "end_at": "2025-11-24T21:30:00Z",
    "winner_id": null,
    "winner_type": "Team",
    "has_bracket": true,
    "prizepool": "5,000 United States Dollar",
    "slug": "cs-go-cct-europe-european-contenders-2-3-2025-playoffs",
    "detailed_stats": false,
    "live_supported": false,
    "league_id": 5232,
    "serie_id": 9863,
    "modified_at": "2025-11-10T18:35:02Z"
  }
}
```

---

## 📺 Dados de Stream

### Streams List
```json
{
  "streams_list": [
    {
      "main": true,           // true = stream primária
      "language": "en",       // Idioma
      "official": true,       // true = stream oficial
      "embed_url": "https://player.kick.com/cct_cs2",  // URL para player embarcado
      "raw_url": "https://kick.com/cct_cs2"            // URL bruta
    },
    {
      "main": false,
      "language": "ru",
      "official": false,
      "embed_url": "https://player.twitch.tv/?channel=eplcs_ru",
      "raw_url": "https://www.twitch.tv/eplcs_ru"
    }
  ]
}
```

**Uso**: Priorizar stream com `main: true`. Se não houver, usar primeira com `official: true`.

---

## 📊 Dados de Resultado (Results)

### Results Array
```json
{
  "results": [
    {
      "team_id": 135092,    // FK → opponents[0].opponent.id
      "score": 0            // Placares no match (não per-game)
    },
    {
      "team_id": 137476,
      "score": 2
    }
  ]
}
```

**⚠️ CRÍTICO**: Este é o score **do match**, não individual dos games!  
- Formato: Best-of-3 (BO3) → scores vão de 0-2
- Em RUNNING: Pode estar 1-1, 1-0, etc
- Em FINISHED: Um time terá 2 (vencedor)

Para scores individuais dos games, ver `games[i].status` e `games[i].winner`.

---

## 🎥 Dados Live/Transmissão

### Live Object
```json
{
  "live": {
    "supported": false,               // true = API tem dados live para este match
    "url": null,                      // URL do stream live (raramente preenchido)
    "opens_at": null                  // Hora que stream abre (raramente preenchido)
  }
}
```

**Nota**: Na prática, `supported` é sempre false para CS2. Usar `streams_list` para links reais.

---

## 🔄 Variações Completas por Endpoint

### UPCOMING (`/csgo/matches/upcoming`)
```json
{
  "status": "not_started",
  "begin_at": "2025-11-17T15:30:00Z",           // ✅ SEMPRE preenchido
  "end_at": null,
  "scheduled_at": "2025-11-17T15:30:00Z",
  "original_scheduled_at": "2025-11-17T15:30:00Z",
  "winner": null,
  "winner_id": null,
  "games": [
    { "status": "not_started", "complete": false, "begin_at": null, "end_at": null, ... }
  ],
  "results": [{ "team_id": X, "score": 0 }, { "team_id": Y, "score": 0 }]
}
```

### RUNNING (`/csgo/matches/running`)
```json
{
  "status": "running",
  "begin_at": "2025-11-17T18:02:01Z",           // ✅ Hora real de início
  "end_at": null,
  "scheduled_at": "2025-11-17T18:00:00Z",      // Hora planejada
  "original_scheduled_at": "2025-11-17T18:00:00Z",
  "winner": null,
  "winner_id": null,
  "games": [
    { "status": "finished", "complete": true, "begin_at": "...", "end_at": "...", "winner": {...} },
    { "status": "finished", "complete": true, "begin_at": "...", "end_at": "...", "winner": {...} },
    { "status": "running", "complete": false, "begin_at": "...", "end_at": null, "winner": {id: null} }
  ],
  "results": [{ "team_id": X, "score": 1 }, { "team_id": Y, "score": 1 }]  // Score atual
}
```

### FINISHED (`/csgo/matches/past?filter[status]=finished`)
```json
{
  "status": "finished",
  "begin_at": null,                            // ⚠️ null!
  "end_at": null,                              // ⚠️ null!
  "scheduled_at": null,                        // ⚠️ null!
  "original_scheduled_at": null,               // ⚠️ null!
  "winner": { "id": 135505, "name": "RED Canids Academy", ... },  // ✅ Preenchido
  "winner_id": 135505,                         // ✅ Preenchido
  "games": [
    { "status": "finished", "complete": true, "begin_at": null, "end_at": null, "winner": {...}, ... }
  ],
  "results": [{ "team_id": X, "score": 0 }, { "team_id": Y, "score": 2 }]  // Final
}
```

### CANCELED (`/csgo/matches/past?filter[status]=canceled`)
```json
{
  "status": "canceled",
  "begin_at": null,
  "end_at": null,
  "scheduled_at": null,
  "original_scheduled_at": null,
  "winner": null,                              // Cancelado = sem vencedor
  "winner_id": null,
  "games": [],                                 // ⚠️ Pode estar vazio!
  "results": [...]                            // Pode ter scores parciais
}
```

---

## 🛡️ Tratamento de Edge Cases

### Caso 1: Dark Mode Images Ausentes
```json
{
  "image_url": "https://...",
  "dark_mode_image_url": null  // ⚠️ Pode ser null!
}
```
**Solução**: Sempre checar null antes de usar dark_mode_image_url. Fallback para image_url.

### Caso 2: Acronym Vazio/Null
```json
{
  "acronym": null,   // ⚠️ Pode ser null
  "name": "THUNDER dOWNUNDER"
}
```
**Solução**: Usar `acronym || name.substring(0, 3).toUpperCase()` para fallback.

### Caso 3: Location Vazio
```json
{
  "location": "",    // ⚠️ Pode ser vazio
  "name": "Washington"
}
```
**Solução**: Tratar "" como "Unknown" ou exibir sem país.

### Caso 4: Begin_At Null em Finished
```json
{
  "status": "finished",
  "begin_at": null,  // ⚠️ Não posso saber quando começou!
  "games": [
    { "begin_at": null, "end_at": null, ... }  // ⚠️ Nada aqui também!
  ]
}
```
**Solução**: Para matches históricos, usar `modified_at` como proxy de tempo. Informar ao usuário que data exata é desconhecida.

### Caso 5: Prizepool Ausente
```json
{
  "prizepool": null         // ⚠️ Pode ser null
}
```
**Solução**: Exibir "Prize pool: N/A" se null.

### Caso 6: Forfeit (Vitória sem competição)
```json
{
  "forfeit": true,
  "games": [
    { "forfeit": true, "winner": { "id": 135505 }, ... }
  ]
}
```
**Solução**: Adicionar badge "Forfeit" ou "W.O." (Walkover) no embed.

---

## 📡 Headers de Contexto

Sempre analisar:
1. **X-Rate-Limit-Remaining**: Parar se < 50 (limite hora).
2. **X-Total**: Verificar se há mais páginas.
3. **Link**: Seguir `rel="next"` para paginação.
4. **X-Request-Id**: Incluir em logs para debug com PandaScore.

---

## ✅ Checklist de Processamento

Ao receber dados da API:

- [ ] Validar `status` (not_started | running | finished | canceled)
- [ ] Se UPCOMING: Usar `begin_at`, agendar lembrete
- [ ] Se RUNNING: Verificar quais games completaram, atualizar score
- [ ] Se FINISHED: Usar `winner_id` e `results` para resultado final
- [ ] Sempre validar `opponents[0]` e `opponents[1]` existem
- [ ] Conferir `image_url` e fallback para dark_mode_image_url se null
- [ ] Verificar `forfeit` flag
- [ ] Conferir X-Rate-Limit-Remaining antes de próxima chamada

---

## 🔗 Endpoints Resumidos

| Endpoint | Params | Status Esperado | Campos Temporais |
|----------|--------|-----------------|------------------|
| `/upcoming` | `per_page=10` | `not_started` | `begin_at` ✅, `end_at` ❌ |
| `/running` | `per_page=10` | `running` | `begin_at` ✅, `end_at` ❌ |
| `/past?filter[status]=finished` | `per_page=10` | `finished` | Todos ❌ |
| `/past?filter[status]=canceled` | `per_page=10` | `canceled` | Todos ❌ |

---

## 📝 Referência Rápida

```python
# Pattern de verificação segura:

def get_team_name(opponent_obj):
    return opponent_obj.get('acronym') or opponent_obj.get('name', 'Unknown')

def get_team_image(opponent_obj):
    return opponent_obj.get('dark_mode_image_url') or opponent_obj.get('image_url')

def get_match_start_time(match):
    if match['status'] in ['not_started', 'running']:
        return match['begin_at']
    else:
        return match['modified_at']  # Fallback

def get_match_score(match):
    if match['results']:
        return f"{match['results'][0]['score']} - {match['results'][1]['score']}"
    return "TBD"
```

