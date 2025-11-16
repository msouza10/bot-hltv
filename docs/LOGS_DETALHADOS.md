# 📋 LOGS DETALHADOS - Sistema de Notificações

## ✅ O Que Foi Adicionado

### 1. **Logs de Agendamento** (`src/services/notification_manager.py`)

Quando você usa `/notificacoes ativar:true`, agora mostra:

```
[INICIALIZAÇÃO]
✅ Partida 12345: Começa em 23:45:30
  ✅ Agendado: 60min ANTES | Lembrete em: 23:45:30
  ✅ Agendado: 30min ANTES | Lembrete em: 00:15:30
  ✅ Agendado: 15min ANTES | Lembrete em: 00:30:30
  ✅ Agendado: 5min ANTES  | Lembrete em: 00:40:30
  ✅ Agendado: 0min ANTES  | Lembrete em: 00:45:30
✓ Partida 12345: 5 lembretes agendados
```

### 2. **Logs de Verificação** (A cada minuto)

O loop de lembretes verifica a cada minuto e mostra:

```
🔍 Verificando lembretes pendentes...
⏰ VERIFICAÇÃO DE LEMBRETES | Total pendentes: 5 | Hora: 14:32:45
  ⏳ Partida 12345 (60min): Faltam 45m 30s
  ⏳ Partida 12346 (30min): Faltam 25m 10s
  🚀 ENVIANDO: Partida 12347 - Lembrete de 5 minutos
  ✅ Marcado como enviado: Partida 12347 (5min)
  ✅ Marcado como enviado: Partida 12348 (0min)
✅ Ciclo de lembretes concluído: 2 enviados
```

### 3. **Logs de Envio** (Com detalhes de erro)

Quando tenta enviar uma notificação:

```
[NOTIF] Iniciando envio para guild 123456789, partida 12345
[NOTIF] ✅ Guild encontrada: Meu Servidor
[NOTIF] Canal ID encontrado: 987654321
[NOTIF] ✅ Canal encontrado: #notificacoes
[NOTIF] ✅ ENVIADA: Guild 123456789 | Partida 12345 | 60min | MSG ID: 999888777
```

Ou se houver erro:

```
[NOTIF] ❌ Guild 123456789 não encontrada no bot
[NOTIF] ⚠️ Guild 123456789 não tem canal de notificações configurado
[NOTIF] ❌ Canal 987654321 não encontrado no bot
[NOTIF] ❌ Erro ao enviar notificação: KeyError: 'opponent'
```

### 4. **Logs de Inicialização** (`src/bot.py`)

Agora mostra claramente quando tudo está rodando:

```
============================================================
✅ BOT CONECTADO como: HLTV Bot (ID: 123456789)
   Servidores: 1 | Ping: 45ms
============================================================
📋 SERVIDORES CONECTADOS:
   • Meu Servidor (ID: 987654321)
🎮 Status: Assistindo partidas de CS2

[CACHE SCHEDULER]
⏰ Iniciando agendador de cache...
✅ Agendador de cache ATIVO

[NOTIFICATION MANAGER]
📬 Iniciando gerenciador de notificações...
✅ Gerenciador de notificações ATIVO

============================================================
🚀 BOT PRONTO PARA USO
============================================================
```

## 📊 Script de Análise Detalhada

Novo script: `scripts/check_reminders_detailed.py`

```bash
python scripts/check_reminders_detailed.py
```

Mostra:

1. **Lembretes Pendentes**: Quanto tempo falta para cada um
2. **Lembretes Enviados**: Últimos 20 enviados
3. **Resumo por Tipo**: Quantos de cada tipo (60, 30, 15, 5, 0 min)
4. **Estatísticas**: Cobertura de partidas

Exemplo de output:

```
[1️⃣ LEMBRETES PENDENTES]
⏳ Total de lembretes pendentes: 5

  #1 | ⏳ Aguardando
       • Partida: 12345 (Liquid vs FaZe)
       • Tipo: 60 minutos antes
       • Agendado para: 23:45:30
       • Falta: 45m 30s
       • Guild: 123456789 | ID Lembrete: 1

[3️⃣ RESUMO POR TIPO DE LEMBRETE]
  🔔 60 minutos: 50 total | 50 pendentes
  🟡 30 minutos: 50 total | 50 pendentes
  🟠 15 minutos: 50 total | 50 pendentes
  🟡 5 minutos: 50 total | 50 pendentes
  🔴 0 minutos: 50 total | 50 pendentes
```

## 🔍 Como Debugar Agora

### 1. **Verificar Agendamento**
```bash
# Ver logs do bot enquanto usa /notificacoes ativar:true
# Procure por: "Partida X: Y lembretes agendados"
```

### 2. **Verificar Lembretes Pendentes**
```bash
python scripts/check_reminders_detailed.py
# Veja quanto tempo falta para cada lembrete
```

### 3. **Verificar Envio**
```bash
# Se vê "ENVIANDO: Partida X" mas não recebi a mensagem:
# Procure por "[NOTIF]" nos logs do bot
# Pode estar faltando canal ou permissões
```

### 4. **Problemas Comuns**

#### Problema: "Nenhum lembrete agendado"
```
Causa: /notificacoes não foi executado
Solução: Execute /notificacoes ativar:true
```

#### Problema: "Lembretes agendados mas não são enviados"
```
Causa: Loop de verificação não está rodando
Solução: Veja se "✅ Gerenciador de notificações ATIVO" aparece nos logs
```

#### Problema: "⚠️ Guild 123456789 não tem canal configurado"
```
Causa: Você não rodou /canal-notificacoes
Solução: Execute /canal-notificacoes canal:#notificacoes
```

#### Problema: "❌ Canal 987654321 não encontrado"
```
Causa: Canal foi deletado ou bot não tem acesso
Solução: Configure outro canal com /canal-notificacoes
```

## 📈 Acompanhar o Fluxo Completo

Quando você ativa notificações para uma partida que começa em 1 hora:

1. **Comando**: `/notificacoes ativar:true`
   ```
   Log: "Partida 12345: 5 lembretes agendados"
   ```

2. **1 hora - Lembretes são verificados a cada minuto**
   ```
   Log: "⏳ Partida 12345 (60min): Faltam 45m 30s"
   ```

3. **Quando chega o horário**
   ```
   Log: "🚀 ENVIANDO: Partida 12345 - Lembrete de 60 minutos"
   Log: "[NOTIF] ✅ ENVIADA: Guild 123456789 | Partida 12345 | MSG ID: 999"
   ```

4. **Mensagem aparece no Discord**
   ```
   [Embed com 🔔 "Partida começando em 1 hora"]
   ```

## 🎯 Resumo Das Melhorias

✅ Logs mostram **exatamente** quando lembretes são agendados  
✅ Logs mostram **quanto tempo falta** para cada lembrete  
✅ Logs mostram **se foi enviado ou por que falhou**  
✅ Script de debug mostra **status em tempo real**  
✅ Erros agora aparecem com **contexto completo**  

Agora você consegue rastrear ONDE e POR QUÊ um lembrete não foi enviado!
