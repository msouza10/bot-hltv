# 🗺️ ROADMAP - Melhorias Futuras do Bot

## Visão Geral

Documento com todas as melhorias, funcionalidades e pontos de evolução para o bot-hltv!

---

## 📊 Prioridades

```
ALTA (🔴)      → Implementar em breve (impacto alto, complexidade baixa)
MÉDIA (🟡)     → Quando tiver tempo (impacto médio, complexidade média)
BAIXA (🟢)     → Futuro distante (impacto baixo ou complexidade alta)
```

---

## 🎯 FASE 1: FILTROS E BUSCAS (Próximo Trimestre)

### 1.1 Filtrar por Time 🔴 ⭐⭐
```
/partidas-time time:SK futuras:5
```
**O quê**: Mostrar partidas de um time específico  
**Por quê**: Usuários querem seguir times preferidos  
**Onde**: cogs/matches.py  
**Onde**: Adicionar coluna team_filter em cache  
**Complexidade**: Média

### 1.2 Filtrar por Torneio 🟡 ⭐⭐
```
/partidas-torneio torneio:ESL futuras:5
```
**O quê**: Mostrar partidas de um torneio  
**Por quê**: Seguir campeonatos específicos (ESL, BLAST, PGL)  
**Onde**: cogs/matches.py  
**Implementação**: Query DB por tournament_name + autocomplete  
**Complexidade**: Média

### 1.3 Filtrar por Região 🟡 ⭐
```
/partidas-liga liga:BR
```
**O quê**: Partidas da sua região  
**Por quê**: Horários e times mais relevantes  
**Onde**: cogs/matches.py  
**Complexidade**: Fácil

### 1.4 Busca Flexível 🟡 ⭐⭐⭐
```
/buscar query:SK_vs_FURIA
```
**O quê**: Buscar com string flexível  
**Por quê**: UX mais intuitiva  
**Onde**: cogs/matches.py  
**Implementação**: Full-text search + fuzzy matching  
**Complexidade**: Difícil

---

## 👤 FASE 2: PERSONALIZAÇÕES (Próximo Trimestre)

### 2.1 Sistema de Favoritos 🔴 ⭐⭐
```
/favorito adicionar:SK
/favoritos
```
**O quê**: Salvar times/torneios preferidos  
**Por quê**: Personalizações por usuário  
**Onde**: Nova tabela user_favorites  
**Implementação**: Destacar ⭐ nos embeds  
**Complexidade**: Média

### 2.2 Notificações por Time 🔴 ⭐⭐
```
/notificar-time time:SK
```
**O quê**: Notificações apenas de times seguidos  
**Por quê**: Menos notificações, só as que importam  
**Onde**: Modificar notification_manager.py  
**Implementação**: Filtro em match_reminders  
**Complexidade**: Média

### 2.3 Configurar Horários de Notificação 🟡 ⭐⭐
```
/notificacao-config horarios:30,10,5
```
**O quê**: Customizar minutos antes da notificação  
**Por quê**: Usuários controlam notificações  
**Onde**: Nova coluna user_notification_schedule  
**Complexidade**: Média

### 2.4 Modo Silencioso 🟡 ⭐⭐
```
/silencioso de:23h ate:8h
```
**O quê**: Não notificar em certos horários  
**Por quê**: Não acordar de madrugada  
**Onde**: quiet_hours_start/end em DB  
**Implementação**: Verificar horário antes de enviar  
**Complexidade**: Média

---

## 📈 FASE 3: ESTATÍSTICAS (Segundo Trimestre)

### 3.1 Stats de Times 🟡 ⭐⭐⭐
```
/stats-time time:SK
```
**O quê**: Vitórias, derrotas, maps, win-rate  
**Por quê**: Entender performance dos times  
**Onde**: cogs/matches.py  
**Implementação**: Agregar dados de match_results + gráficos ASCII  
**Complexidade**: Difícil

### 3.2 Stats de Torneios 🟢 ⭐⭐
```
/stats-torneio torneio:ESL
```
**O quê**: Info geral do torneio  
**Por quê**: Contexto sobre campeonatos  
**Complexidade**: Média

### 3.3 Rankings de Times 🟢 ⭐⭐
```
/rankings
```
**O quê**: Top 10 times por vitórias/elo  
**Por quê**: Ver times em ranking  
**Complexidade**: Média

### 3.4 Stats por Mapa 🟢 ⭐⭐
```
/stats-mapa mapa:Inferno
```
**O quê**: Qual time melhor em qual mapa  
**Por quê**: Análise de meta  
**Complexidade**: Média

---

## 🎮 FASE 4: INTERATIVIDADE (Segundo Trimestre)

### 4.1 Votações/Predictions 🟢 ⭐⭐
```
/prever time1:SK time2:FURIA
```
**O quê**: Usuários votam em quem ganha  
**Por quê**: Gamificação e engajamento  
**Onde**: Nova tabela user_predictions  
**Implementação**: Reactions para votar  
**Complexidade**: Média

### 4.2 Ranking de Preditores 🟢 ⭐⭐⭐
```
/rank-preditores
```
**O quê**: Leaderboard de quem acertou mais  
**Por quê**: Competição amigável  
**Complexidade**: Difícil

### 4.3 Buttons Interativos 🟡 ⭐⭐
**O quê**: Buttons em embeds para:
- ✅ Acompanhar (favoritos)
- 🔔 Notificar
- 📊 Ver stats
- 🏆 Prever resultado

**Por quê**: UX melhor, menos comandos  
**Onde**: embeds.py + event handlers  
**Complexidade**: Média

---

## 💾 FASE 5: HISTÓRICO E DADOS (Futuro)

### 5.1 Histórico de Partidas 🟢 ⭐
```
/historico
```
**O quê**: Últimas 20 partidas que viu  
**Por quê**: Rastrear interesse  
**Implementação**: Nova tabela user_history  
**Complexidade**: Fácil

### 5.2 Export de Dados 🟢 ⭐⭐
```
/exportar formato:json
```
**O quê**: Exportar em JSON/CSV  
**Por quê**: Usar dados em outro lugar  
**Complexidade**: Média

### 5.3 VOD/Replay Links 🟢 ⭐
**O quê**: Links de replay nos embeds  
**Por quê**: Acesso rápido a replays  
**Complexidade**: Fácil (se API suportar)

---

## 🎨 FASE 6: VISUAL E UX (Próximo Trimestre)

### 6.1 Cores por Status 🟡 ⭐
```
🔴 Futuras: Vermelho
🟠 Ao Vivo: Laranja
🟢 Finalizadas: Verde
⚪ Canceladas: Cinza
```
**Por quê**: Mais visual, identifica status rápido  
**Complexidade**: Fácil

### 6.2 Countdown em Embeds 🟡 ⭐
```
"Começa em: 2h 30min"
"Ao vivo há: 45min"
```
**Por quê**: Urgência visual  
**Complexidade**: Fácil

### 6.3 Modo Compacto vs Detalhado 🟡 ⭐⭐
```
/view-mode compacto
/view-mode detalhado
```
**Por quê**: Flexibilidade visual  
**Complexidade**: Média

### 6.4 Themes/Skins 🟢 ⭐⭐
```
/theme dark
/theme light
```
**Por quê**: Personalização visual  
**Complexidade**: Média

---

## 🔗 FASE 7: INTEGRAÇÕES (Futuro)

### 7.1 Liquipedia Integration 🟡 ⭐⭐⭐
**O quê**: Stats e histórico dos times  
**Por quê**: Mais contexto sobre times  
**Implementação**: Liquipedia API ou scraping  
**Complexidade**: Difícil

### 7.2 HLTV Stats 🟡 ⭐⭐⭐
**O quê**: Stats de jogadores, HLTV rating  
**Por quê**: Informações de players importantes  
**Complexidade**: Difícil

### 7.3 Múltiplos Canais 🟡 ⭐⭐
```
/notificacoes-multiplos canais:canal1,canal2
```
**Por quê**: Em servidor grande, não perder notificações  
**Complexidade**: Média

---

## 🔧 FASE 8: MONITORAMENTO (Próximo Trimestre)

### 8.1 Dashboard /status 🟡 ⭐⭐
```
/status
→ Uptime: 30d 5h
→ Partidas em cache: 106
→ Reminders agendados: 42
→ Próxima atualização: 2m
→ Ping API: 150ms
→ Latência Discord: 50ms
→ DB Status: OK
```
**Por quê**: Saber status do bot  
**Complexidade**: Média

### 8.2 Alerts de Offline 🟡 ⭐⭐
**O quê**: Notificar se bot ficar offline > 1h  
**Por quê**: Alertar sobre problemas  
**Complexidade**: Média

### 8.3 Cache Stale Alerts 🟡 ⭐
**O quê**: Alertar se cache > 30min sem update  
**Por quê**: Saber quando dados podem estar ruins  
**Complexidade**: Fácil

### 8.4 Performance Metrics 🟡 ⭐⭐⭐
**O quê**: Tempo médio de resposta, taxa de erro, cache hit rate  
**Por quê**: Identificar gargalos  
**Implementação**: Prometheus ou banco local  
**Complexidade**: Difícil

---

## 📈 FASE 9: ESCALABILIDADE (Futuro)

### 9.1 Multi-Servidor 🔴 ⭐⭐⭐
**O quê**: Configurações diferentes por servidor  
**Por quê**: ESSENCIAL para produção com múltiplos servidores  
**Implementação**: Nova tabela guild_config  
**Complexidade**: Difícil

### 9.2 Multi-Idioma 🟡 ⭐⭐
```
Idiomas: PT-BR, EN, ES
/idioma es
```
**Por quê**: Alcançar mais usuários  
**Implementação**: i18n library + tradução de embeds  
**Complexidade**: Média (trabalhoso)

### 9.3 Timezone Support 🟡 ⭐⭐
```
/timezone America/Sao_Paulo
```
**Por quê**: Horários corretos para cada usuário  
**Implementação**: Converter tempos nos embeds  
**Complexidade**: Média

### 9.4 Database Sharding 🟢 ⭐⭐⭐⭐
**O quê**: Separar dados por servidor/região  
**Por quê**: Escalabilidade infinita se DB crescer muito  
**Complexidade**: MUITO Difícil (futura)

---

## 🔒 FASE 10: SEGURANÇA (Próximo Trimestre)

### 10.1 Rate Limiting 🟡 ⭐⭐
```
Max 10 comandos/minuto por usuário
```
**Por quê**: Evitar spam  
**Implementação**: Decorador + cache  
**Complexidade**: Média

### 10.2 Permissões por Rol 🟡 ⭐
```
/cache-refresh (só admin)
/notificacoes-multiplos (só admin)
```
**Por quê**: Evitar abuse  
**Complexidade**: Fácil

### 10.3 Audit Log 🟢 ⭐
**O quê**: Log de todos os comandos  
**Por quê**: Rastreabilidade  
**Implementação**: Nova tabela audit_log  
**Complexidade**: Fácil

---

## ✅ FASE 11: TESTES (Segundo Trimestre)

### 11.1 Unit Tests 🟡 ⭐⭐
**O quê**: Testes de:
- pandascore_service.py (parsing)
- embeds.py (formatação)
- cache_manager.py (lógica)

**Framework**: pytest  
**Por quê**: Confiança no código  
**Complexidade**: Média

### 11.2 Integration Tests 🟡 ⭐⭐⭐
**O quê**: Testes ponta a ponta (API → DB → Discord)  
**Framework**: pytest com fixtures  
**Por quê**: Confiança em deploys  
**Complexidade**: Difícil

### 11.3 Load Testing 🟢 ⭐⭐⭐
**O quê**: 1000 usuários simultâneos  
**Framework**: locust  
**Por quê**: Saber se escala  
**Complexidade**: Difícil

---

## 📚 FASE 12: DOCUMENTAÇÃO (Contínuo)

### 12.1 Wiki de Usuário 🟡 ⭐⭐
**O quê**: Documentação completa para usuários  
**Conteúdo**: Como usar cada comando, FAQ, troubleshooting, vídeos  
**Por quê**: Usuários entendem como usar  
**Complexidade**: Média (muita escrita)

### 12.2 API Documentation 🟡 ⭐⭐
**O quê**: Documentação para devs  
**Framework**: Sphinx  
**Por quê**: Fácil para outros devs contribuírem  
**Complexidade**: Média

### 12.3 Contributing Guide 🟢 ⭐
**O quê**: CONTRIBUTING.md  
**Conteúdo**: PR workflow, code style, commit format  
**Por quê**: Abrir para contribuições  
**Complexidade**: Fácil

---

## 📋 PRIORIZAÇÃO RECOMENDADA

### Trimestre 1 (Próximas 3 meses) 🔴🟡
1. **Filtrar por Time** - Impacto alto, complexidade média
2. **Sistema de Favoritos** - Impacto alto, complexidade média
3. **Notificações por Time** - Impacto alto, complexidade média
4. **Cores por Status** - Impacto médio, complexidade fácil
5. **Dashboard /status** - Impacto médio, complexidade média
6. **Multi-Servidor Setup** - Impacto CRÍTICO, complexidade difícil

### Trimestre 2 (3-6 meses) 🟡
7. **Multi-Idioma** - Impacto médio, complexidade média
8. **Stats de Times** - Impacto médio, complexidade difícil
9. **Unit Tests** - Impacto médio, complexidade média
10. **Buttons Interativos** - Impacto médio, complexidade média

### Futuro (6+ meses) 🟢
11. **Votações/Predictions** - Impacto baixo, complexidade média
12. **Integrações Externas** - Impacto baixo, complexidade difícil
13. **Database Sharding** - Impacto muito alto (escala infinita), complexidade muito difícil

---

## 🎯 Critério de Sucesso

Cada funcionalidade deve ter:
- ✅ Comando bem definido
- ✅ Mensagens/embeds claros
- ✅ Error handling robusto
- ✅ Testes básicos
- ✅ Documentação
- ✅ Sem quebrar features existentes

---

## 📞 Próximos Passos

1. **Hoje**: Revisar este roadmap
2. **Esta semana**: Escolher TOP 3 funcionalidades para o mês
3. **Este mês**: Implementar TOP 3
4. **Este trimestre**: Completar FASE 1 + 2 + parte da FASE 8

---

## 📊 Legenda de Complexidade

| ⭐ | Significa |
|----|-----------|
| ⭐ | Fácil (< 2h) |
| ⭐⭐ | Média (2-8h) |
| ⭐⭐⭐ | Difícil (8-24h) |
| ⭐⭐⭐⭐ | Muito Difícil (> 24h) |

---

**Versão**: 1.0  
**Data**: 2025-11-16  
**Status**: 📋 Pronto para Implementação

Ver também: `plan/TODO.md` para checklist detalhado
