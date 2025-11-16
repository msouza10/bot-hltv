## 🎮 Bot HLTV — Notificações CS2 (Python / Nextcord)

Bot de Discord para enviar notificações automáticas de partidas de Counter-Strike 2 (CS2) usando a PandaScore API. Esta versão está alinhada ao stack Python/Nextcord e ao roadmap definido nos arquivos `plan/` e `docs/`.

> Status: ✅ Produção — MVP com notificações 24h, 1h, ao vivo e resultado final.

---

## Visão rápida

- Notificações: 24h antes, 1h antes, quando partida inicia (live) e quando termina (resultado).
- Filtros por times favoritos por servidor (guild).
- Fácil configuração por slash commands (`/setup`, `/seguir`, `/partidas`).

---

## Stack principal

- Linguagem: Python 3.10+
- Discord framework: Nextcord >= 2.4
- API de dados: PandaScore (CS2 Fixtures)
- HTTP assíncrono: aiohttp
- Scheduler: APScheduler
- DB: SQLite com libSQL (Turso) backend
- Cache: 3-tier (memory → DB → API fallback)

---

## 📁 Estrutura do Projeto

```
bot-hltv/
├── src/                      # ⭐ Código fonte principal (necessário para rodar bot)
│   ├── bot.py               # Entrada principal
│   ├── cogs/                # Comandos Discord (/partidas, /aovivo, /resultados)
│   ├── database/            # Cache e banco de dados
│   ├── services/            # Serviços (API PandaScore, scheduler, notificações)
│   └── utils/               # Utilitários (embeds formatados)
│
├── scripts/                 # Scripts de teste/debug/setup
│   ├── init_db.py          # Inicializar banco de dados
│   ├── validate_cache_full.py
│   ├── preview_embed.py
│   ├── check_*.py          # Verificação de API e cache
│   └── analyze_*.py        # Análise de dados
│
├── docs/                    # 📚 Documentação completa
│   ├── COMECE_AQUI.txt
│   ├── GUIA_*.md           # Guias de uso
│   ├── MELHORIAS_*.md      # Documentação de features
│   ├── ARQUITETURA_*.md    # Arquitetura e design
│   └── *.md/*.txt          # Especificações e resumos
│
├── data/                    # 💾 Banco de dados
│   └── bot.db              # Cache de partidas (SQLite)
│
├── logs/                    # 📝 Logs de execução
│
├── plan/                    # 📋 Planejamento
│   ├── DUVIDAS.md
│   └── TODO.md
│
├── README.md               # Este arquivo
├── SETUP.md                # Guia de setup
├── requirements.txt        # Dependências Python
├── setup.py                # Setup do projeto
├── .env                    # Configurações (token Discord, etc)
├── .env.example            # Exemplo de .env
└── .gitignore
```

---

## 🚀 Quick Start

### 1️⃣ Setup Inicial
```bash
# Clonar repo
git clone <repo-url>
cd bot-hltv

# Criar virtual env
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados (primeira vez)
python scripts/init_db.py
```

### 2️⃣ Configurar .env
```bash
# Copiar template
copy .env.example .env

# Editar com seus tokens:
# DISCORD_TOKEN=seu_token_aqui
# PANDASCORE_TOKEN=seu_token_pandascore
```

### 3️⃣ Rodar Bot
```bash
python -m src.bot
```

### 4️⃣ Em Discord
```
/partidas 5        # Ver próximas 5 partidas
/aovivo            # Ver partidas ao vivo
/resultados 1 5    # Ver últimos 5 resultados
```

---

## 📚 Documentação

### Para Iniciantes
- **`SETUP.md`** - Setup completo passo a passo
- **`docs/COMECE_AQUI.txt`** - Comeco rápido
- **`docs/PRIMEIROS_PASSOS.md`** - Guia do desenvolvedor

### Referência Técnica
- **`docs/ESPECIFICACAO_TECNICA.md`** - Spec completa
- **`docs/ARQUITETURA_CACHE.md`** - Como funciona o cache
- **`docs/FLUXO_CACHE_EXPLICADO.md`** - Fluxo de dados
- **`docs/COMPARACAO_APIS.md`** - Análise de APIs

### Features e Melhorias
- **`docs/MELHORIAS_THUMBNAIL_v3.md`** - Sistema de thumbnails
- **`docs/MELHORIAS_EMBEDS_FINAIS.md`** - Formatação de embeds
- **`docs/GUIA_STATUS_PARTIDA.md`** - Estados de partida

### Planejamento
- **`plan/TODO.md`** - Tarefas futuras
- **`plan/DUVIDAS.md`** - Questões em aberto

---

## 🛠️ Ferramentas

### Scripts de Teste

**Validar cache:**
```bash
python scripts/validate_cache_full.py
```

**Preview de embeds:**
```bash
python scripts/preview_embed.py
```

**Testar API PandaScore:**
```bash
python scripts/check_api_structure.py
```

**Inicializar DB (se necessário):**
```bash
python scripts/init_db.py
```

---

## 📂 O que está onde?

| Pasta | Conteúdo | Necessário? |
|-------|---------|-----------|
| `src/` | Código principal do bot | ✅ SIM |
| `scripts/` | Scripts de teste/debug | ❌ Não |
| `docs/` | Documentação completa | ❌ Referência |
| `data/` | Banco de dados (bot.db) | ✅ SIM |
| `logs/` | Logs de execução | ❌ Auto-gerado |
| `plan/` | Planejamento/TODO | ❌ Referência |

---

## ⚙️ Configuração

### Arquivo: `.env`

```env
# Token do Bot Discord
DISCORD_TOKEN=your_discord_token_here

# ID do servidor (Guild) - opcional
DISCORD_GUILD_ID=your_guild_id

# Token da API PandaScore
PANDASCORE_TOKEN=your_pandascore_token

# URL do banco de dados Turso
DATABASE_URL=libsql://...
```

Ver `SETUP.md` para instruções detalhadas.

---

## 🎯 Funcionalidades

✅ **Comandos Discord**
- `/partidas N` - Próximas N partidas
- `/aovivo` - Partidas ao vivo agora
- `/resultados N M` - Últimos M resultados

✅ **Notificações Automáticas**
- 24 horas antes da partida
- 1 hora antes da partida
- Quando partida começa (ao vivo)
- Quando partida termina

✅ **Cache Inteligente**
- 3-tier: memória (< 100ms) → DB (< 3s) → API (fallback)
- 106 partidas sincronizadas
- Atualização automática a cada 15 minutos

✅ **Embeds Profissionais**
- Thumbnail com logo do time vencedor
- Background com imagem da liga
- Informações completas (mapas, placar, forfeit, etc)

✅ **Gerenciamento de Status**
- Partidas futuras
- Ao vivo
- Acabadas
- Canceladas/Adiadas

---

## 🔍 Verificar Tudo Está Funcionando

```bash
# 1. Verificar cache
python scripts/validate_cache_full.py

# 2. Ver embeds formatados
python scripts/preview_embed.py

# 3. Rodar bot
python -m src.bot

# 4. Em Discord, executar comando
/resultados 1 5
```

---

## 📝 Estrutura de Código - `src/`

```
src/
├── bot.py                    # Entrada principal (inicializa bot)
│
├── cogs/                     # Comandos Discord
│   ├── matches.py           # /partidas, /aovivo, /resultados
│   ├── notifications.py     # Sistema de notificações
│   └── ping.py              # /ping (health check)
│
├── database/                # Cache e BD
│   ├── cache_manager.py     # 3-tier cache (memory → DB → API)
│   ├── build_db.py
│   ├── debug_cache.py
│   └── schema.sql           # Schema SQLite
│
├── services/                # Serviços
│   ├── pandascore_service.py # Integração API PandaScore
│   ├── cache_scheduler.py    # Atualiza cache a cada 15min
│   └── notification_manager.py
│
└── utils/                   # Utilitários
    ├── embeds.py            # Formatação de embeds Discord
    └── __init__.py
```

---

## 📊 Dados em Cache

O bot sincroniza automaticamente:

- **50 partidas futuras**
- **2 partidas ao vivo**
- **20 partidas finalizadas**
- **20 partidas canceladas/adiadas**

**Total: ~92 partidas atualizadas a cada 15 minutos**

Campos sincronizados:
- ID, Status, Liga (com imagem)
- Série, Torneio, Tipo de match
- Times, Placar, Mapas
- Forfeit, Draw, Versão do jogo
- Data de início/fim

---

## ❓ FAQ

**P: Onde fico o banco de dados?**  
R: Em `data/bot.db` — não deletar!

**P: Como mudar o intervalo de atualização do cache?**  
R: Em `src/services/cache_scheduler.py`, linha ~50

**P: Como adicionar notificações customizadas?**  
R: Ver `docs/GUIA_NOTIFICACOES.md`

**P: Posso hospedar em um servidor?**  
R: Sim! Ver `docs/DEPLOYMENT.md` (se existir) ou `SETUP.md`

---

## 🐛 Problemas Comuns

**Bot não inicia:**
- Verificar `.env` com token correto
- Executar `python scripts/init_db.py`
- Ver logs em `logs/`

**Sem partidas em cache:**
- Rodar `python scripts/validate_cache_full.py`
- Verificar token da PandaScore
- Verificar conexão com internet

**Embeds cortados:**
- Verificar tamanho de descrição em `src/utils/embeds.py`
- Embeds Discord têm limite de 4096 caracteres

---

## 📞 Próximos Passos

1. ✅ Testar em Discord: `/resultados 1 5`
2. 📚 Ler documentação em `docs/`
3. 🛠️ Customizar conforme necessário
4. 🚀 Deploy em produção

---

## 📝 Documentação importante

- Visão geral: `docs/VISAO_GERAL.md`
- Especificação técnica: `docs/ESPECIFICACAO_TECNICA.md`
- Primeiros passos (setup local): `docs/PRIMEIROS_PASSOS.md`
- Quick start: `docs/QUICK_START.md`
- Comparação de APIs: `docs/COMPARACAO_APIS.md`
- Pesquisa de APIs: `docs/PESQUISA_API.md`
- Roadmap / TODO: `plan/TODO.md`

---

## Como começar (desenvolvedor)

Siga o guia completo em `docs/PRIMEIROS_PASSOS.md`. Resumo rápido:

```bash
# clonar
git clone <repo-url>
cd bot-hltv

# criar venv e ativar
python -m venv venv
source venv/bin/activate

# instalar dependências
pip install -r requirements.txt

# copiar .env e editar (DISCORD_TOKEN, PANDASCORE_API_KEY, DATABASE_PATH)
cp .env.example .env

# rodar o bot em modo desenvolvimento
python -m src.bot
```

---

## Estrutura do projeto (resumo)

```
bot-hltv/
├── docs/              # Documentação do projeto
├── plan/              # Planejamento e TODOs
├── src/               # Código fonte Python
│   ├── bot.py         # Ponto de entrada
│   ├── cogs/          # Cogs (comandos)
│   ├── services/      # PandaScore client, notification service
│   ├── database/      # Schema e camada aiosqlite
│   └── utils/         # Embeds, logger, helpers
├── data/              # Arquivos gerados (bot.db)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Contribuições

Contribuições muito bem-vindas. Use branches para features e abra PRs com descrição.

---

## Licença

MIT (a definir) — sugerido para projetos open-source.

---

## Contato

- Issues no repositório
- Mensagens no canal de suporte (quando disponível)

---

Obrigado — vamos transformar isso em algo útil para a comunidade CS2!
