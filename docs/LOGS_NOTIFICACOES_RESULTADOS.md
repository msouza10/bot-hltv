# 📋 Logs de Notificações de Resultados

## ✅ SIM! Os logs aparecem!

As notificações de resultados terão **EXATAMENTE** o mesmo padrão de logging que os lembretes.

---

## 🔍 O QUE VOCÊ VERÁ NOS LOGS

### 1️⃣ **Detecção de Transição (a cada 1 minuto)**

```
2025-11-16 14:50:00 - src.services.cache_scheduler - INFO - 🔍 Verificação rápida de resultados (cache apenas)...
2025-11-16 14:50:01 - src.services.cache_scheduler - INFO -    📊 1 partida(s) em running sem atualização recente
2025-11-16 14:50:02 - src.services.cache_scheduler - INFO -    📊 Checando contra 15 partidas finished
2025-11-16 14:50:03 - src.services.cache_scheduler - WARNING - 🔥 TRANSIÇÃO RÁPIDA DETECTADA: Match 1234567
2025-11-16 14:50:03 - src.services.cache_scheduler - WARNING -    Status agora: finished
2025-11-16 14:50:04 - src.services.cache_scheduler - WARNING - 🎯 1 transição(ões) confirmada(s)!
2025-11-16 14:50:05 - src.services.cache_scheduler - INFO -    ✅ Cache atualizado: 1234567
2025-11-16 14:50:05 - src.services.cache_scheduler - INFO -       📬 Notificação agendada para guild 1188166184760254594
```

### 2️⃣ **Agendamento de Resultado**

```
2025-11-16 14:50:05 - src.services.notification_manager - INFO - 📬 Resultado agendado: Guild 1188166184760254594, Match 1234567
```

### 3️⃣ **Loop de Verificação (a cada 1 minuto)**

```
2025-11-16 14:51:00 - src.services.notification_manager - INFO - 🔍 [VERIFICAÇÃO] Checando notificações - 14:51:00
```

### 4️⃣ **Envio de Resultado**

```
2025-11-16 14:51:01 - src.services.notification_manager - INFO -    📊 1 notificação(ões) de resultado pendente(s)
2025-11-16 14:51:01 - src.services.notification_manager - INFO -    🚀 ENVIANDO RESULTADO: Match 1234567 para Guild 1188166184760254594
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-INIT] Iniciando envio para guild 1188166184760254594, match 1234567
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-OK] ✅ Guild encontrada: 'noobs server'
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-OK] ✅ Canal ID: 1189631098759335014
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-OK] ✅ Canal: #resultados
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-OK] ✅ Dados parseados
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-OK] ✅ Embed criado
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       [RESULT-SUCCESS] ✅ ENVIADA COM SUCESSO!
2025-11-16 14:51:02 - src.services.notification_manager - INFO -          Guild: noobs server (1188166184760254594)
2025-11-16 14:51:02 - src.services.notification_manager - INFO -          Canal: #resultados (1189631098759335014)
2025-11-16 14:51:02 - src.services.notification_manager - INFO -          Partida: 1234567
2025-11-16 14:51:02 - src.services.notification_manager - INFO -          MSG ID: 1234567890123456789
2025-11-16 14:51:02 - src.services.notification_manager - INFO -       ✅ Resultado marcado como enviado
2025-11-16 14:51:02 - src.services.notification_manager - INFO -    📈 Total de resultados enviados: 1
2025-11-16 14:51:02 - src.services.notification_manager - INFO - ✅ [VERIFICAÇÃO CONCLUÍDA] 14:51:02
```

---

## 📊 FLUXO COMPLETO NOS LOGS

```
┌─────────────────────────────────────────────────────────────┐
│             EXEMPLO COMPLETO NO LOG                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 14:50:00 - Partida termina                                  │
│ 14:50:03 - Detecta transição (check_finished_task)        │
│            └─ "🔥 TRANSIÇÃO RÁPIDA DETECTADA"             │
│            └─ "🎯 1 transição(ões) confirmada(s)!"         │
│                                                              │
│ 14:50:05 - Agenda resultado                                │
│            └─ "📬 Resultado agendado"                      │
│                                                              │
│ 14:51:00 - Loop de verificação                             │
│            └─ "🔍 [VERIFICAÇÃO] Checando notificações"    │
│                                                              │
│ 14:51:01 - Detecta resultado pendente                       │
│            └─ "📊 1 notificação(ões) de resultado pend"   │
│                                                              │
│ 14:51:02 - Envia para Discord                              │
│            └─ "🚀 ENVIANDO RESULTADO"                      │
│            └─ "[RESULT-OK] ✅ Guild encontrada"            │
│            └─ "[RESULT-OK] ✅ Canal encontrado"            │
│            └─ "[RESULT-SUCCESS] ✅ ENVIADA COM SUCESSO!"  │
│                                                              │
│ 14:51:02 - Verifica conclusão                              │
│            └─ "✅ [VERIFICAÇÃO CONCLUÍDA]"                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Emojis nos Logs

| Emoji | Significado |
|-------|-----------|
| 🔍 | Verificação iniciada |
| 📊 | Estatísticas/contagem |
| 🔥 | Evento importante (transição) |
| 🎯 | Confirmação |
| 📬 | Agendamento |
| 🚀 | Envio em andamento |
| ✅ | Sucesso |
| ❌ | Erro |
| ⚠️ | Aviso |
| 🔌 | Desconexão |

---

## 📈 COMPARATIVO: Lembretes vs Resultados

### Logs de LEMBRETE (já existem)
```
🚀 ENVIANDO AGORA: Match 1234567 | 60min antes
   ✅ Sucesso: Lembrete marcado como enviado
   Guild: noobs server (ID: 1188166184760254594)
   Canal: #notificacoes (ID: 1189631098759335014)
```

### Logs de RESULTADO (novo!)
```
🚀 ENVIANDO RESULTADO: Match 1234567 para Guild 1188166184760254594
   ✅ Resultado marcado como enviado
   Guild: noobs server (ID: 1188166184760254594)
   Canal: #notificacoes (ID: 1189631098759335014)
```

---

## 🔧 Onde Aparecem os Logs?

```
/logs/bot.log
```

**Como ver em tempo real**:
```bash
tail -f logs/bot.log
```

**Filtrar apenas resultados**:
```bash
tail -f logs/bot.log | grep -E "RESULTADO|result_notif|TRANSIÇÃO|🔥"
```

**Filtrar lembretes e resultados**:
```bash
tail -f logs/bot.log | grep -E "ENVIANDO|RESULTADO|LEMBRETE"
```

---

## 📝 Verbosidade dos Logs

### 🟢 VERDE: INFO (informações normais)
```
📬 Resultado agendado
🚀 ENVIANDO RESULTADO
✅ Enviada com sucesso
```

### 🟡 AMARELO: WARNING (avisos)
```
🔥 TRANSIÇÃO RÁPIDA DETECTADA
⚠️ Falha ao enviar notificação
```

### 🔴 VERMELHO: ERROR (erros)
```
❌ Guild não encontrada
❌ Canal não configurado
❌ Erro ao parsear JSON
```

---

## ✅ O que Esperar Quando Funcionar

### Timeline dos Logs
```
14:50:03 [INFO] 🔥 TRANSIÇÃO DETECTADA
14:50:05 [INFO] 📬 Resultado agendado
14:51:01 [INFO] 📊 1 notificação de resultado pendente
14:51:02 [INFO] 🚀 ENVIANDO RESULTADO
14:51:02 [INFO] [RESULT-SUCCESS] ✅ ENVIADA COM SUCESSO!
14:51:02 [INFO] ✅ [VERIFICAÇÃO CONCLUÍDA]
```

---

## 🎯 Resumo

✅ **SIM, os logs aparecem!**

- Detecção de resultado: Mostrado com 🔥
- Agendamento: Mostrado com 📬
- Envio: Mostrado com 🚀
- Sucesso: Mostrado com ✅
- Timing: Exatamente como lembretes

**Logs completos e com todos os detalhes!** 📋
