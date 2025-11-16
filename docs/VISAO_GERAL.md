# 🤖 Bot HLTV - Discord Notificações CS2

## 📖 Visão Geral do Projeto

Bot do Discord desenvolvido para enviar notificações automáticas sobre partidas oficiais de Counter-Strike 2 (CS2), utilizando dados da PandaScore API.

---

## 🎯 Objetivo

Criar um bot que mantenha a comunidade de CS2 informada sobre:
- **24h antes** - Lembrete de partidas importantes
- **1h antes** - Aviso final antes do início
- **Ao vivo** - Notificação quando a partida começar
- **Resultado** - Placar final após término da partida

Com sistema de times favoritos para notificações personalizadas.

---

## 👥 Público-Alvo

- Comunidades de CS2 no Discord
- Fãs de esports que seguem cena competitiva
- Servidores de times/organizações
- Grupos de amigos que assistem partidas juntos

---

## ✨ Funcionalidades Principais

### 🔔 Sistema de Notificações Automáticas
- **24 horas antes**: Lembrete antecipado da partida
- **1 hora antes**: Aviso próximo ao início
- **Ao Vivo**: Quando partida mudar status para "running"
- **Finalizada**: Placar e resultado completo
- **Filtros**: Apenas times favoritos (se configurado)

### 🎮 Comandos do Bot
- `/setup` - Configurar canal de notificações
- `/seguir [time]` - Adicionar time aos favoritos
- `/desseguir [time]` - Remover time dos favoritos
- `/meustimes` - Listar times favoritos configurados
- `/partidas` - Listar próximas partidas (hoje/amanhã)
- `/aovivo` - Ver partidas acontecendo agora
- `/resultados` - Resultados recentes
- `/ajuda` - Documentação completa de comandos
- `/sobre` - Informações sobre o bot
# 🤖 Bot HLTV — Visão Geral (resumida)

Bot para notificações de partidas de CS2 no Discord. Foco em confiabilidade, baixa latência para notificações e configuração por servidor.

## Objetivo

Entregar notificações nas janelas: 24h, 1h, live e resultado. Usuários podem seguir times para receber apenas notificações relevantes.

## Público-alvo

- Comunidades e servidores de esports
- Usuários que acompanham partidas competitivas de CS2

## Funcionalidades (resumo)

- Notificações automáticas (24h, 1h, live, resultado)
- Filtros por times favoritos
- Slash commands para configuração e consultas
- Persistência simples (SQLite)

## Arquitetura (resumo)

- Linguagem: Python 3.10+
- Biblioteca Discord: Pycord
- Data source: PandaScore API
- Scheduler: APScheduler (polling)
- DB: SQLite

Estrutura principal:

```
src/
├─ bot.py
├─ cogs/
├─ services/ (pandascore, notifications)
├─ database/ (db, schema)
└─ utils/ (embeds, logger)
```

## Fluxo resumido

1. Polling (APScheduler) chama PandaScore
2. Parse e armazenamento em cache
3. Calcular notificações por guild
4. Enviar embed via Pycord e registrar envio

## Observações

- Polling padrão: 15min; live: 5min
- Evitar duplicidade via `notifications_sent`
- Conversão de horários para UTC e exibição local por guild

**Última atualização:** 15 de novembro de 2025
└── README.md
