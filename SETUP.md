# 🚀 Setup do Bot HLTV

## Instalação Rápida

### 1. Clone o repositório
```bash
git clone <seu-repo>
cd bot-hltv
```

### 2. Crie um ambiente virtual
```bash
python3.13 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com suas credenciais:
# - DISCORD_TOKEN (do Discord Developer Portal)
# - PANDASCORE_API_KEY (de pandascore.com)
# - TESTING_GUILD_ID (seu servidor de testes)
```

### 5. Crie o banco de dados
```bash
python -m src.database.build_db
```

### 6. Rode o bot
```bash
python -m src.bot
```

## 📊 Estrutura do Projeto

```
bot-hltv/
├── src/
│   ├── bot.py                    # Bot principal
│   ├── cogs/
│   │   ├── matches.py            # Comandos de partidas
│   │   └── ping.py               # Comando de teste
│   ├── database/
│   │   ├── build_db.py           # Criar/resetar banco
│   │   ├── cache_manager.py      # Gerenciador de cache
│   │   ├── debug_cache.py        # Debug do cache
│   │   └── schema.sql            # Schema do libSQL
│   ├── services/
│   │   ├── pandascore_service.py # Cliente da API
│   │   └── cache_scheduler.py    # Tasks agendadas
│   └── utils/
│       └── embeds.py             # Formatação de embeds
├── requirements.txt              # Dependências
├── .env.example                  # Exemplo de .env
└── .gitignore                    # Arquivos ignorados
```

## 🔧 Dependências

- **nextcord** ≥2.6.0 - Discord bot framework (suporte Python 3.13)
- **aiohttp** ≥3.9.0 - Cliente HTTP assíncrono
- **libsql-client** ≥0.3.0 - Cliente libSQL (Turso)
- **python-dotenv** ≥1.0.0 - Carregamento de .env
- **python-dateutil** ≥2.8.2 - Manipulação de datas

## 🎯 Funcionalidades

- ✅ Slash commands: `/ping`, `/partidas`, `/aovivo`, `/resultados`
- ✅ Cache libSQL com retenção de 24h
- ✅ Tasks agendadas (15min atualização completa, 5min lives)
- ✅ API PandaScore integration
- ✅ Debug utilities e statistics

## 🗑️ .gitignore

Os seguintes arquivos NÃO são commitados:
- `venv/` - Ambiente virtual
- `.env` - Variáveis de ambiente (use `.env.example`)
- `*.db` - Arquivos de banco de dados
- `data/` - Diretório de dados locais
- `logs/` - Arquivos de log
- `__pycache__/` - Cache Python

## 📝 Variáveis de Ambiente

```bash
# Discord
DISCORD_TOKEN=your_token
CLIENT_ID=your_id
CLIENT_SECRET=your_secret
PUBLIC_KEY=your_key

# Database (libSQL)
LIBSQL_URL=file:./data/bot.db
LIBSQL_AUTH_TOKEN=  # Vazio para banco local

# Guild (testes)
TESTING_GUILD_ID=your_guild_id

# API
PANDASCORE_API_KEY=your_api_key
```

## 🚨 Troubleshooting

**Erro: "no such table"**
```bash
# Recrie o banco
python -m src.database.build_db --reset
```

**Erro: "threads can only be started once"**
- Não ocorre mais! Migramos para libSQL que não tem issues de threading

**Ver estatísticas do cache**
```bash
python -m src.database.debug_cache
```

---
**Desenvolvido com ❤️ para CS2 HLTV**
