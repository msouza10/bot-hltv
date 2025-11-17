# 🎯 Checklist: Validação do Scheduler em Produção

## ✅ PRÉ-INICIALIZAÇÃO (Antes de iniciar o bot)

```
☐ 1. Verificar configuração do scheduler
     $ python scripts/check_scheduler_config.py
     Resultado esperado: ✅ Todos os checks devem passar
     Tempo: ~5 segundos

☐ 2. Verificar status do cache atual
     $ python scripts/check_cache_status.py
     Resultado esperado: Qualquer número de matches (pode estar vazio)
     Tempo: ~3 segundos

☐ 3. Verificar logs antigos
     $ tail -20 logs/bot.log
     Procure por: Nenhum erro de DEADLOCK ou TIMEOUT
     
☐ 4. Confirmar variáveis de ambiente
     $ cat .env | grep DISCORD_TOKEN
     $ cat .env | grep PANDASCORE_API_KEY
     Resultado esperado: Ambas presentes
     
☐ 5. Ativar virtual environment
     $ source venv/bin/activate
     Resultado esperado: Prompt mostra (venv)

☐ TUDO OK? Prossiga para INICIALIZAÇÃO →
```

---

## 🚀 INICIALIZAÇÃO (Iniciar o bot)

```
☐ 1. Iniciar o bot
     $ python -m src.bot
     Resultado esperado: 
     - Bot conecta ao Discord
     - Mostra: "✓ Agendador iniciado com Discord Tasks!"
     - Mostra: "• Atualização completa: a cada 3 minutos"
     - Mostra: "• Verificação de resultados: a cada 1 minuto"
     - Mostra: "• Primeira execução: em 2 segundos"
     
     ⏱️ Deixe o bot rodando por pelo menos 5 minutos

☐ 2. Em OUTRO TERMINAL: Monitorar logs
     $ tail -f logs/bot.log | grep -E 'scheduler|Atualiz|verific|RUNNING|FINISHED'
     
     Resultado esperado (por tempo de execução):
     
     +2s  → 🔄 Iniciando atualização completa do cache...
            ✓ 50 partidas próximas obtidas
            ✓ X partidas ao vivo obtidas
            ✓ 20 partidas finalizadas obtidas
            🔍 Verificação rápida de resultados
     
     +1min → 🔍 Verificação rápida de resultados (2ª exec)
     
     +2min → 🔍 Verificação rápida de resultados (3ª exec)
     
     +3min → 🔄 Iniciando atualização completa (2ª exec)
             ✓ XX partidas próximas obtidas
             🔍 Verificação rápida (4ª exec)
     
     +4min → 🔍 Verificação rápida (5ª exec)
     
     +5min → 🔍 Verificação rápida (6ª exec)

☐ 3. EM OUTRO TERMINAL: Validar cache após 3+ minutos
     $ python scripts/check_cache_status.py
     
     Resultado esperado:
     - ✅ Cache age < 3 minutos
     - ✅ Total matches: 70-80
     - ✅ Upcoming: ~50, Running: ~1-3, Finished: ~20
     - ✅ Last update: menos de 3 minutos

☐ TUDO OK? Prossiga para TESTES EM DISCORD →
```

---

## 🎮 TESTES EM DISCORD

```
☐ 1. Testar /aovivo (Partidas ao vivo)
     Esperado:
     - Mostra partidas em status "running"
     - Cada partida tem streams com hyperlinks [channel_name](url)
     - Formato: BO3 - Best Of
     - Streams mostram: 🇧🇷 [Twitch](url) ⭐
     
☐ 2. Testar /partidas (Próximas partidas)
     Esperado:
     - Mostra 5 próximas partidas (status "upcoming")
     - Cada uma tem horário de início
     - Formato: BO3 - Best Of
     - Não há streams (ou estão em branco)
     
☐ 3. Testar /resultados (Últimos resultados)
     Esperado:
     - Mostra últimas partidas finalizadas
     - Cada uma mostra: Vencedor vs Perdedor 2-0
     - Status: Finished
     - Sem streams (match finalizado)

☐ 4. Testar /notificacoes (Configurar notificações)
     Esperado:
     - Bot responde com opções de configuração
     - Pode ativar/desativar notificações
     - Mostra canal de notificações configurado

☐ TUDO FUNCIONANDO? Prossiga para VALIDAÇÃO AVANÇADA →
```

---

## 🔬 VALIDAÇÃO AVANÇADA (Verificações detalhadas)

```
☐ 1. Forçar atualização manual
     $ python scripts/force_cache_update.py
     
     Resultado esperado:
     - Executa em < 10 segundos
     - Mostra: ✅ 50 partidas próximas obtidas
     - Mostra: ✅ X partidas ao vivo obtidas
     - Mostra: ✅ 20 partidas finalizadas obtidas
     - Mostra: 📊 Novo estado do cache: Upcoming: 50, Running: X, Finished: 20
     - SEM travamentos ou timeouts
     - SEM erros de DEADLOCK

☐ 2. Verificar detalhes de lock
     $ grep -n "async with _cache_update_lock" src/services/cache_scheduler.py
     
     Resultado esperado:
     - 2 ocorrências (update_all_matches e update_live_matches)
     - cache_streams NÃO tem lock aninhado (verificar cache_manager.py)

☐ 3. Monitorar cache por 10 minutos
     $ watch -n 10 'python scripts/check_cache_status.py'
     
     Resultado esperado:
     - Last update sempre < 10 minutos (tipicamente < 3 min)
     - Total matches diminui/cresce conforme partidas progridem
     - Sem erro de timeout ou deadlock

☐ 4. Verificar logs para erros
     $ grep -i "error\|exception\|timeout" logs/bot.log | tail -20
     
     Resultado esperado:
     - ZERO erros relacionados a cache_manager.py
     - ZERO erros de "deadlock" ou "lock"
     - ZERO erros de "timeout" (ou timeout muito raramente)

☐ 5. Testar cenário de carga (30+ minutos)
     - Deixar bot rodando por 30 minutos
     - Executar /aovivo, /partidas, /resultados a cada 5 minutos
     - Monitorar logs para problemas
     
     Resultado esperado:
     - Bot responde em < 3 segundos
     - Cache atualiza a cada 3 minutos
     - Sem travamentos ou erros

☐ TUDO VALIDADO? Prossiga para CONCLUSÃO →
```

---

## ✨ CONCLUSÃO & PRÓXIMAS AÇÕES

```
☐ 1. Bot está respondendo aos comandos rapidamente?
     ✓ SIM → Ótimo! Performance está OK

☐ 2. Cache está sendo renovado a cada 3 minutos?
     ✓ SIM → Scheduler está funcionando corretamente

☐ 3. Partidas ao vivo mostram streams com hyperlinks?
     ✓ SIM → Embeds estão formatados corretamente

☐ 4. Nenhum erro nos logs?
     ✓ SIM → Sistema está estável

☐ 5. Tudo funcionou como esperado?
     ✓ SIM → BOT PRONTO PARA PRODUÇÃO! 🎉
     ✗ NÃO → Consulte seção "SOLUÇÃO DE PROBLEMAS" abaixo

```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### ❌ Problema: Logs mostram "SQLITE_BUSY" ou "database locked"

**Causa**: Deadlock em cache_manager.py (cache_streams tentando adquirir lock já preso)

**Verificar**:
```bash
grep "async with self._lock" src/database/cache_manager.py | wc -l
# Deve retornar: 1 (apenas em cache_matches, NÃO em cache_streams)
```

**Solução**:
```bash
# Editar src/database/cache_manager.py
# Remover "async with self._lock:" de cache_streams()
# Ver seção 5 da documentação anterior para detalhes
```

---

### ❌ Problema: Logs mostram "asyncio.TimeoutError"

**Causa**: Timeout de 1 segundo é muito curto para queries

**Verificar**:
```bash
grep "timeout=" src/database/cache_manager.py
# Deve mostrar: timeout=10.0 em _update_memory_cache
```

**Solução**:
```bash
# Aumentar timeout de 1.0 para 10.0 em _update_memory_cache
# Ver seção anterior para detalhes
```

---

### ❌ Problema: Cache não está sendo atualizado há 10+ minutos

**Causa**: Tasks não estão rodando ou estão travadas

**Verificar**:
```bash
# 1. Ver se bot está realmente rodando
ps aux | grep "python.*src.bot"

# 2. Ver logs de inicialização
tail -100 logs/bot.log | grep -i "scheduler\|task\|iniciado"

# 3. Testar cache manual
python scripts/force_cache_update.py
```

**Solução**:
- Se `force_cache_update.py` funciona: Tasks podem estar desabilitadas, reiniciar bot
- Se `force_cache_update.py` trava: Há deadlock, ver solução anterior

---

### ❌ Problema: Streams mostram "Other Unknown" em vez de plataforma

**Causa**: format_streams_field() não conseguindo extrair plataforma

**Verificar**:
```bash
grep "Other Unknown" logs/bot.log
```

**Verificação avançada**:
```bash
python scripts/check_cache_content.py
# Ver se field "platform" está populado na tabela match_streams
```

**Solução**: Já deve estar corrigido na versão atual
- `format_streams_field()` extrai automaticamente platform de raw_url
- Se ainda falhar, verificar se raw_url está presente no BD

---

### ❌ Problema: Hyperlinks de streams não funcionam em Discord

**Causa**: Formato markdown incorreto ou URL inválida

**Verificar**:
```bash
grep "\[" logs/bot.log | grep "channel"
# Deve mostrar: [channel_name](url)
```

**Solução**:
- Verificar se URLs têm formato correto (https://...)
- Verificar se channel_name não está vazio
- Testar formato: `[channel_name](url)` manualmente em Discord

---

## 📞 SUPORTE RÁPIDO

| Problema | Comando | Resultado Esperado |
|----------|---------|-------------------|
| Bot não liga | `python -m src.bot` | Conecta em <5s |
| Logs com erro | `tail -f logs/bot.log` | Sem "error" ou "exception" |
| Cache travado | `python scripts/force_cache_update.py` | Completa em <10s |
| Status do cache | `python scripts/check_cache_status.py` | Age < 3 min, 70-80 matches |
| Scheduler config | `python scripts/check_scheduler_config.py` | ✅ Todos os checks |

---

## 📋 CHECKLIST FINAL

```
✅ Scheduler está configurado corretamente
✅ Tasks rodam nos intervalos corretos (3 min e 1 min)
✅ Locks previnem race conditions
✅ Deadlock foi corrigido (cache_streams sem lock)
✅ Timeouts foram ajustados (10 segundos)
✅ Cache é renovado a cada 3 minutos
✅ Embeds mostram streams com hyperlinks
✅ Notificações de resultado funcionam
✅ Bot responde em < 3 segundos
✅ Zero erros nos logs por 30+ minutos

BOT PRONTO PARA PRODUÇÃO! 🎉
```

---

**Data**: 2025-11-17  
**Status**: ✅ Validado  
**Versão**: 1.0
