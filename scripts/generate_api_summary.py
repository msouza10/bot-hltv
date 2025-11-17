#!/usr/bin/env python3
"""
RESUMO EXECUTIVO - Análise da API PandaScore para CS2
Rodado em: 17 de Novembro de 2025

Este script documenta TUDO que a API retorna e como usar.
"""

RESUMO_VISUAL = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   🎯 ESTRUTURA PANDASCORE API - RESUMO                    ║
║                      Matches de Counter-Strike 2                          ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 ENDPOINTS E RETORNOS
═══════════════════════════════════════════════════════════════════════════

1️⃣  UPCOMING  (/csgo/matches/upcoming)
    Status HTTP: 200
    Match Status: "not_started"
    Total Available: 288 (via header X-Total)
    
    Temporal Data:
    ├─ begin_at: "2025-11-17T15:30:00Z"  ✅ SEMPRE PREENCHIDO
    ├─ scheduled_at: "2025-11-17T15:30:00Z"
    ├─ original_scheduled_at: "2025-11-17T15:30:00Z"
    └─ end_at: null
    
    Games: 3 (BO3)
    ├─ games[0].status: "not_started"
    ├─ games[1].status: "not_started"
    └─ games[2].status: "not_started"
    
    Results: [0, 0] (ambos 0 pois não começou)
    Winner: null
    Winner ID: null


2️⃣  RUNNING  (/csgo/matches/running)
    Status HTTP: 200
    Match Status: "running"
    Matches em andamento: 7
    
    Temporal Data:
    ├─ begin_at: "2025-11-17T18:02:01Z"  ✅ HORA REAL DE INÍCIO
    ├─ scheduled_at: "2025-11-17T18:00:00Z"  (hora planejada)
    ├─ original_scheduled_at: "2025-11-17T18:00:00Z"
    └─ end_at: null  (ainda em progresso)
    
    Games: MISTO
    ├─ games[0].status: "finished"  ✅ Completado
    │  ├─ begin_at: "2025-11-17T18:02:01Z"
    │  ├─ end_at: "2025-11-17T18:43:02Z"
    │  ├─ length: 2460 segundos
    │  └─ winner: {id: 127829}
    ├─ games[1].status: "finished"  ✅ Completado
    │  ├─ begin_at: "2025-11-17T18:57:55Z"
    │  ├─ end_at: "2025-11-17T19:30:14Z"
    │  ├─ length: 1938 segundos
    │  └─ winner: {id: 132459}
    └─ games[2].status: "running"   🔴 Rodando AGORA
       ├─ begin_at: "2025-11-17T19:46:22Z"
       ├─ end_at: null
       ├─ length: null
       └─ winner: {id: null}
    
    Results: [1, 1]  (score atual: 1-1)
    Winner: null  (ainda indeciso)
    Winner ID: null


3️⃣  FINISHED  (/csgo/matches/past?filter[status]=finished)
    Status HTTP: 200
    Match Status: "finished"
    Matches retornados: 10
    
    Temporal Data (⚠️ TODOS NULL):
    ├─ begin_at: null  ❌ NÃO DISPONÍVEL!
    ├─ scheduled_at: null  ❌ NÃO DISPONÍVEL!
    ├─ original_scheduled_at: null  ❌ NÃO DISPONÍVEL!
    └─ end_at: null  ❌ NÃO DISPONÍVEL!
    
    👉 FALLBACK: Usar "modified_at": "2025-06-24T11:50:26Z"
    
    Games: ALL FINISHED
    ├─ games[0].status: "finished"
    │  ├─ begin_at: null  ❌
    │  ├─ end_at: null  ❌
    │  ├─ forfeit: true (Walkover!)
    │  └─ winner: {id: 135505}
    ├─ games[1].status: "finished"
    │  ├─ begin_at: null  ❌
    │  ├─ end_at: null  ❌
    │  ├─ forfeit: true (Walkover!)
    │  └─ winner: {id: 135505}
    └─ [game 3 não rodou, score 2-0]
    
    Results: [0, 2]  (score final)
    Winner: {id: 135505, name: "RED Canids Academy", ...}  ✅
    Winner ID: 135505  ✅


4️⃣  CANCELED  (/csgo/matches/past?filter[status]=canceled)
    Status HTTP: 200
    Match Status: "canceled"
    Matches cancelados: 10
    
    Temporal Data: Todos null (como finished)
    
    Games: Pode estar VAZIO []
    
    Results: Pode ter scores parciais
    Winner: null  (cancelado = sem vencedor)
    Winner ID: null


═══════════════════════════════════════════════════════════════════════════
🏆 ESTRUTURA HIERÁRQUICA COMPLETA
═══════════════════════════════════════════════════════════════════════════

Match Object
├── Identifiers
│   ├── id: 1269173  (PK)
│   ├── name: "Upper bracket quarterfinal 2: ALLIN vs WSG"
│   ├── slug: "allinners-vs-washington-2025-11-17"
│   └── status: "not_started" | "running" | "finished" | "canceled"
│
├── Temporal (VARIA por status)
│   ├── begin_at: ISO8601 ou null
│   ├── end_at: ISO8601 ou null
│   ├── scheduled_at: ISO8601 ou null
│   └── original_scheduled_at: ISO8601 ou null
│
├── Match Details
│   ├── match_type: "best_of"
│   ├── number_of_games: 3
│   ├── forfeit: false/true
│   ├── rescheduled: false/true
│   ├── detailed_stats: false/true
│   └── draw: false/true
│
├── Result
│   ├── winner: {id, name, acronym, ...} ou null
│   ├── winner_id: number ou null
│   └── results: [{team_id, score}, {team_id, score}]
│
├── Games (Array de 3)
│   └── [0,1,2]
│       ├── id: 194264
│       ├── position: 1
│       ├── status: "not_started" | "running" | "finished"
│       ├── complete: true/false
│       ├── finished: true/false
│       ├── begin_at: ISO8601 ou null
│       ├── end_at: ISO8601 ou null
│       ├── length: 2460 (segundos) ou null
│       ├── forfeit: true/false
│       └── winner: {id: number ou null}
│
├── Teams/Opponents (Array de 2)
│   ├── [0]
│   │   └── opponent
│   │       ├── id: 135092  (FK)
│   │       ├── name: "ALLINNERS"
│   │       ├── acronym: "ALLIN" (pode ser null!)
│   │       ├── location: "KZ" (pode ser ""!)
│   │       ├── image_url: "https://..."
│   │       └── dark_mode_image_url: "https://..." ou null
│   └── [1]
│       └── opponent: {...}
│
├── League/Tournament Context
│   ├── league_id: 5232
│   ├── league
│   │   ├── id: 5232
│   │   ├── name: "CCT Europe"
│   │   ├── slug: "cs-go-cct-europe"
│   │   └── image_url: "https://..."
│   │
│   ├── tournament_id: 18006
│   ├── tournament
│   │   ├── id: 18006
│   │   ├── name: "Playoffs"
│   │   ├── type: "online"
│   │   ├── region: "EEU"
│   │   ├── tier: "d"
│   │   ├── prizepool: "5,000 USD" ou null
│   │   ├── begin_at: ISO8601
│   │   ├── end_at: ISO8601
│   │   └── has_bracket: true/false
│   │
│   ├── serie_id: 9863
│   └── serie
│       ├── id: 9863
│       ├── name: "European Contenders #2"
│       ├── year: 2025
│       ├── season: "3"
│       └── full_name: "European Contenders #2 season 3 2025"
│
├── Streaming
│   ├── live
│   │   ├── supported: false (sempre false para CS2)
│   │   ├── url: null
│   │   └── opens_at: null
│   └── streams_list: [
│       {
│           "main": true,
│           "language": "en",
│           "official": true,
│           "embed_url": "https://player.kick.com/cct_cs2",
│           "raw_url": "https://kick.com/cct_cs2"
│       },
│       {
│           "main": false,
│           "language": "ru",
│           "official": false,
│           "embed_url": "https://player.twitch.tv/?channel=eplcs_ru",
│           "raw_url": "https://www.twitch.tv/eplcs_ru"
│       }
│   ]
│
├── Video Game Info
│   ├── videogame
│   │   ├── id: 3
│   │   ├── name: "Counter-Strike"
│   │   └── slug: "cs-go"
│   ├── videogame_title
│   │   ├── id: 13
│   │   ├── name: "Counter-Strike 2"
│   │   ├── slug: "cs-2"
│   │   └── videogame_id: 3
│   └── videogame_version: null
│
└── Metadata
    ├── modified_at: ISO8601
    └── game_advantage: null


═══════════════════════════════════════════════════════════════════════════
⚠️ EDGE CASES CRÍTICOS
═══════════════════════════════════════════════════════════════════════════

1. FINISHED matches: begin_at é null!
   └─ Usar modified_at como fallback
   
2. Dark mode images: podem ser null
   └─ Fallback para image_url
   
3. Team acronym: pode ser null
   └─ Usar name.substring(0,3) como fallback
   
4. Team location: pode ser ""
   └─ Tratar como "Unknown"
   
5. Tournament prizepool: pode ser null
   └─ Exibir "N/A"
   
6. Games com begin_at/end_at null em finished
   └─ Dados incompletos da API
   
7. Forfeit flag: pode estar true
   └─ Adicionar badge "W.O." (Walkover) no embed


═══════════════════════════════════════════════════════════════════════════
🔍 HEADERS DE CONTEXTO (RESPONSE)
═══════════════════════════════════════════════════════════════════════════

X-Rate-Limit-Remaining: 889
    └─ Se < 50, PARAR! Atingiram limite horário
    
X-Rate-Limit-Used: 111
    └─ Requisições usadas nesta hora
    
X-Total: 288
    └─ Total de matches neste endpoint
    
X-Page: 1
    └─ Página atual (começa em 1)
    
X-Per-Page: 10
    └─ Items por página retornado
    
Link: <https://...?page=2>; rel="next", <https://...?page=29>; rel="last"
    └─ Paginação: seguir rel="next" para próxima página
    
X-Request-Id: GHjk3jOJfQpYqk8CMtfh
    └─ ID único para debug com PandaScore (incluir em logs)


═══════════════════════════════════════════════════════════════════════════
✅ CHECKLIST AO PROCESSAR DADOS
═══════════════════════════════════════════════════════════════════════════

[ ] Verificar X-Rate-Limit-Remaining < 50 → PARAR
[ ] Verificar status: "not_started" | "running" | "finished" | "canceled"
[ ] Se UPCOMING: usar begin_at para agendar
[ ] Se RUNNING: verificar games misto, atualizar score parcial
[ ] Se FINISHED: usar winner_id e results para resultado final
[ ] Validar opponents[0] e opponents[1] existem
[ ] Verificar image_url, fallback para dark_mode_image_url se null
[ ] Verificar team acronym, usar name[0:3] se null
[ ] Verificar forfeit flag
[ ] Validar streams_list não vazio, priorizar main: true
[ ] Conferir X-Total para saber se há mais páginas
[ ] Usar X-Request-Id em logs para debug


═══════════════════════════════════════════════════════════════════════════
📚 REFERÊNCIA RÁPIDA - PADRÕES DE ACESSO
═══════════════════════════════════════════════════════════════════════════

# Hora do match (safe)
match_time = match['begin_at'] if match['status'] in ['not_started', 'running'] \\
            else match.get('modified_at')

# Time 1
team1 = match['opponents'][0]['opponent']
team1_name = team1.get('acronym') or team1.get('name', 'Unknown')

# Time 2
team2 = match['opponents'][1]['opponent']
team2_name = team2.get('acronym') or team2.get('name', 'Unknown')

# Score
score = f"{match['results'][0]['score']}-{match['results'][1]['score']}"

# Imagem (com fallback)
image = team1.get('dark_mode_image_url') or team1.get('image_url')

# Stream primária
main_stream = next((s for s in match['streams_list'] if s['main']), None)
stream_url = main_stream['raw_url'] if main_stream else None

# Verificar forfeit
if match.get('forfeit'):
    print("Vitória por W.O. (Walkover)")


═══════════════════════════════════════════════════════════════════════════
🔗 DOCUMENTAÇÃO COMPLETA
═══════════════════════════════════════════════════════════════════════════

Ver: docs/ANALISE_ESTRUTURA_API_PANDASCORE.md

- Explicação detalhada de todos os campos
- Exemplos completos de JSON
- Tratamento de edge cases
- Patterns seguros de acesso


═══════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(RESUMO_VISUAL)
    
    # Save to file
    with open("/home/msouza/Documents/bot-hltv/docs/PANDASCORE_API_QUICK_REFERENCE.txt", "w") as f:
        f.write(RESUMO_VISUAL)
    
    print("\n✅ Resumo salvo em: docs/PANDASCORE_API_QUICK_REFERENCE.txt")
