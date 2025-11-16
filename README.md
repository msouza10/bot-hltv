git clone [url-do-repositorio]
## 🎮 Bot HLTV — Notificações CS2 (Python / Pycord)

Bot de Discord para enviar notificações automáticas de partidas de Counter-Strike 2 (CS2) usando a PandaScore API. Esta versão está alinhada ao stack Python/Pycord e ao roadmap definido nos arquivos `plan/` e `docs/`.

> Status: Em desenvolvimento — MVP focado em notificações 24h, 1h, ao vivo e resultado final.

---

## Visão rápida

- Notificações: 24h antes, 1h antes, quando partida inicia (live) e quando termina (resultado).
- Filtros por times favoritos por servidor (guild).
- Fácil configuração por slash commands (`/setup`, `/seguir`, `/partidas`).

---

## Stack principal

- Linguagem: Python 3.10+
- Discord framework: Pycord (py-cord) >= 2.4
- API de dados: PandaScore (Fixtures - plano gratuito)
- HTTP assíncrono: aiohttp
- Scheduler: APScheduler
- DB MVP: SQLite (aiosqlite)

---

## Documentação importante

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
