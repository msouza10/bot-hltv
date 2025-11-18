# ✅ Comando /timezone_info Adicionado

## Resumo Executivo

Novo comando Discord `/timezone_info` adicionado ao bot para **exibir** qual timezone está sendo usado no servidor. Complementa o comando existente `/timezone` que é para **configurar**.

---

## 📋 Novo Comando: `/timezone_info`

### Localização
- **Arquivo:** `src/cogs/notifications.py` (linhas 319-430)
- **Cog:** `NotificationsCog`
- **Tipo:** Slash command (sem parâmetros obrigatórios)

### O que faz?

**Exibe informações sobre o timezone atual do servidor:**

```
🌍 Timezone do Servidor
Este servidor está usando America/Sao_Paulo

📍 Informações do Timezone
├─ Timezone: America/Sao_Paulo
├─ Abreviação: BRST
├─ Offset UTC: -03:00
└─ Emoji: 🇧🇷

⏰ Hora Atual neste Timezone
├─ Data: 27/01/2025
└─ Horário: 15:42:30 BRST

📋 O que você vê?
├─ Partidas: Convertidas para BRST
├─ Notificações: Enviadas no horário BRST
├─ Lembretes: Usando BRST
└─ API: Continua usando UTC internamente

🔧 Alterar Timezone
Use /timezone para mudar o timezone do servidor.
```

### Fluxo de Execução

1. **Usuário executa** `/timezone_info` em qualquer canal
2. **Bot fetcha** o timezone do `cache_manager.get_guild_timezone()`
3. **Se timezone não está configurado** → Mostra mensagem informativa com instrução para usar `/timezone`
4. **Se timezone está configurado** → Exibe:
   - Nome completo do timezone
   - Abreviação (ex: BRST, EST, JST)
   - Offset UTC (ex: -03:00, +00:00)
   - Emoji do país
   - **Hora atual neste timezone** (em tempo real)
   - Exemplos de como o bot usa o timezone
5. **Bot loga** a execução com emoji `🌍`

### Exemplos de Saída

#### Cenário 1: Timezone Configurado (America/Sao_Paulo)
```
✅ Exibir:
   Timezone: America/Sao_Paulo
   Abreviação: BRST
   Offset: -03:00
   Hora Atual: 15:42:30 BRST em 27/01/2025
```

#### Cenário 2: Timezone NÃO Configurado
```
🟠 Exibir:
   Mensagem: "Timezone Não Configurado"
   Instrução: Use /timezone para configurar
   Exemplos: America/Sao_Paulo, Europe/London, Asia/Tokyo
```

---

## 🎯 Diferenças: Comandos de Timezone

| Aspecto | `/timezone` | `/timezone_info` |
|---------|-----------|-----------------|
| **Objetivo** | Configurar | Exibir/Consultar |
| **Parâmetros** | `fuso_horario` (obrigatório) | Nenhum |
| **Permissões** | Admin apenas | Qualquer membro |
| **O que faz** | Atualiza BD e valida | Busca e mostra informações |
| **Resposta** | Confirmação + detalhes | Informações + hora atual |

---

## 🔍 Recursos Técnicos

### 1. **Integração com Cache**
```python
timezone = await self.bot.cache_manager.get_guild_timezone(guild_id)
```
- Busca timezone do servidor no banco de dados
- Retorna None se não configurado
- Usa cache interno para performance

### 2. **Informações em Tempo Real**
```python
import datetime
import pytz

tz_obj = pytz.timezone(timezone)
current_time = datetime.datetime.now(tz_obj)
```
- Calcula hora **atual** neste timezone
- Usa biblioteca `pytz` para conversão
- Exibe data e hora formatadas

### 3. **Integração com TimezoneManager**
```python
tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
tz_offset = TimezoneManager.get_timezone_offset(timezone)
tz_emoji = TimezoneManager.get_server_timezone_emoji(timezone)
```
- Reutiliza utilities já validadas
- Consistência com resto do bot
- Abreviações, offsets, emojis

### 4. **Logging com Emoji**
```python
logger.info(f"🌍 /timezone_info: Timezone do servidor = {timezone} (Guild: {guild_id})")
```
- Log em comando (como já implementado)
- Emoji `🌍` para visual consistency
- Inclui guild_id para rastreamento

### 5. **Tratamento de Erros**
- Try/except captura qualquer erro
- Retorna embed de erro se falhar
- Log do erro para troubleshooting

---

## 📝 Logging

### Quando Timezone Existe (Sucesso)
```
🌍 /timezone_info: Timezone do servidor = America/Sao_Paulo (Guild: 123456789)
```

### Quando Timezone Não Existe (Info)
```
🌍 /timezone_info: Timezone não configurado para guild 123456789
```

### Quando Erro Ocorre
```
❌ Erro ao exibir timezone_info: [erro específico]
```

**Para filtrar logs de timezone:**
```bash
tail -f logs/bot.log | grep "🌍"
```

---

## 🧪 Teste Recomendado

### 1. Sem Timezone Configurado
```
Executar: /timezone_info
Esperado: Mensagem "Timezone Não Configurado" com instruções
```

### 2. Com Timezone Configurado
```
Executar: /timezone America/Sao_Paulo
Executar: /timezone_info
Esperado: Mostra "America/Sao_Paulo" com hora atual (ex: 15:42:30 BRST)
```

### 3. Verificar Logs
```bash
grep "🌍 /timezone_info" logs/bot.log
Esperado: Linhas como: "🌍 /timezone_info: Timezone do servidor = America/Sao_Paulo (Guild: ...)"
```

---

## 🔗 Integração com Fluxo Existente

```
┌──────────────────────────────────────┐
│    Usuário no Discord                │
├──────────────────────────────────────┤
│                                      │
│  /timezone [config] ──────┐          │
│                           ↓          │
│  /timezone_info ────→ cache_manager  │
│                           ↓          │
│                      DB (timezone)   │
│                           ↓          │
│  Resposta: Exibe informações + hora  │
└──────────────────────────────────────┘
```

---

## 📊 Resumo de Mudanças

| Item | Antes | Depois |
|------|-------|--------|
| Comandos timezone | 1 (/timezone para config) | 2 (/timezone + /timezone_info) |
| Permissão /timezone_info | N/A | Qualquer membro |
| Logging timezone_info | N/A | ✅ Com emoji 🌍 |
| Visibilidade timezone | Apenas na config | ✅ Comando dedicado |
| Hora em tempo real | N/A | ✅ Exibida ao consultar |

---

## ✅ Checklist de Implementação

- ✅ Comando `/timezone_info` adicionado
- ✅ Integração com `cache_manager.get_guild_timezone()`
- ✅ Integração com `TimezoneManager` (abbr, offset, emoji)
- ✅ Cálculo de hora em tempo real
- ✅ Tratamento de timezone não configurado
- ✅ Tratamento de erros com try/except
- ✅ Logging com emoji 🌍
- ✅ Documentação inline
- ✅ Mensagens informativas
- ✅ Embeds formatados

---

## 🚀 Próximos Passos (Opcional)

1. **Testar em Discord** - Executar `/timezone_info` e verificar resposta
2. **Verificar logs** - Confirmar que emoji 🌍 aparece em logs
3. **Documentar no README** - Adicionar `/timezone_info` à lista de comandos

---

## 📌 Notas Importantes

- O comando `/timezone_info` é **read-only** - não modifica nada
- Pode ser executado por **qualquer membro** (sem permissões admin)
- A hora exibida é **sempre em tempo real** baseado no servidor
- Se timezone não está configurado, instrui usuário a usar `/timezone`
- **Logging consistente** com resto do bot (emoji 🌍)

---

**Status:** ✅ COMPLETO
**Data:** 2025
**Arquivo:** src/cogs/notifications.py (linhas 319-430)
