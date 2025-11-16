# Plano de Tarefas - Bot HLTV (resumido e priorizado)

Este arquivo contém as tarefas principais organizadas por prioridade para o desenvolvimento do MVP em Python/Pycord.

## Prioridade Alta (MVP)
- [ ] 1. Inicializar repositório para Python
  - Criar venv, `requirements.txt`, `.env.example` e `.gitignore`
- [ ] 2. Estrutura básica do projeto
  - Criar diretórios `src/{cogs,services,database,models,utils}`, `data/`, `logs/`, `config/`
- [ ] 3. Setup do bot (Pycord)
  - `src/bot.py` com inicialização, intents e carregamento de cogs
- [ ] 4. Integração com PandaScore
  - `src/services/pandascore_service.py` (aiohttp client, métodos: upcoming, running, past, details)
- [ ] 5. Schema e DB
  - `data/schema.sql` e `src/database/db.py` (aiosqlite)
- [ ] 6. Notificações básicas
  - `src/services/notification_service.py` com APScheduler (polling 15min / 5min)

## Prioridade Média
- [ ] 7. Comandos essenciais (cogs)
  - `/setup`, `/seguir`, `/desseguir`, `/partidas`, `/aovivo`, `/resultados`, `/ajuda`
- [ ] 8. Templates de embeds e assets
  - `src/utils/embeds.py` e tratamento de logos/links
- [ ] 9. Evitar duplicidade
  - `notifications_sent` e checagens antes de enviar

## Prioridade Baixa
- [ ] 10. Logs, métricas e healthcheck
- [ ] 11. Testes unitários básicos (database, parsing, notificações)
- [ ] 12. Documentação de usuário e deploy

## Notas e Assunções
- Uso do plano PandaScore Fixtures (1000 req/h)
- Polling padrão: 15min; live polling: 5min
- MVP foca em servidores públicos/pequenos — escalar depois para Postgres

## Próximos passos imediatos
1. Marcar a tarefa 1 como concluída (criar venv, requirements)
2. Implementar `src/bot.py` mínimo e rodar localmente
3. Implementar `pandascore_service.py` com chamadas reais e testar

---

_Arquivo gerado automaticamente pela atualização de documentação em 15/11/2025._
- [ ] Adicionar bot ao servidor de teste
