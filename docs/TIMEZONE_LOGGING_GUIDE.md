# 🌍 Logging de Timezone - Como Visualizar

## Como Ver o Timezone Sendo Respeitado

Adicionamos logging em **3 pontos estratégicos** para você visualizar exatamente qual timezone está sendo usado:

### 1. **Command Level** (cogs/matches.py)

Quando você usa qualquer um dos 3 comandos, verá no log:

```
🌍 /partidas: Timezone do servidor = America/Sao_Paulo
🌍 /aovivo: Timezone do servidor = America/Sao_Paulo
🌍 /resultados: Timezone do servidor = America/Sao_Paulo
```

**Onde ver**:
- Arquivo: `logs/bot.log`
- Padrão: `[2025-01-15 14:30:45,123] - src.cogs.matches - INFO - 🌍 /partidas: Timezone do servidor = America/Sao_Paulo`

### 2. **Embed Creation Level** (utils/embeds.py)

Quando o embed está sendo criado, verá no log:

```
📍 create_match_embed usando timezone: America/Sao_Paulo
📍 create_result_embed usando timezone: America/Sao_Paulo
```

**Onde ver**:
- Arquivo: `logs/bot.log`
- Padrão: `[2025-01-15 14:30:45,567] - src.utils.embeds - DEBUG - 📍 create_match_embed usando timezone: America/Sao_Paulo`

### 3. **Notification Level** (notification_manager.py)

Quando lembretes ou notificações são enviadas, verá:

```
🌍 /partidas: Timezone do servidor = America/Sao_Paulo
```

---

## 📋 Como Testar

### Opção 1: Testar com Script

```bash
# Testar conversões de timezone
python scripts/test_timezone_display.py
```

Saída esperada:
```
📍 Timezone no servidor:
────────────────────────────────────────────────────────────────────────────────

Testando conversão de: 2025-01-15T18:00:00Z (UTC)

🌍 America/Sao_Paulo
   Discord Timestamp: <t:1736957200:f>
   Abreviação: BRT
   Offset UTC: -03:00

🌍 America/New_York
   Discord Timestamp: <t:1736970800:f>
   Abreviação: EST
   Offset UTC: -05:00

...
```

### Opção 2: Testar em Tempo Real no Discord

1. **Inicie o bot**:
```bash
venv/bin/python -m src.bot
```

2. **Use um dos comandos**:
```
/partidas 3
/aovivo
/resultados
```

3. **Verifique os logs**:
```bash
tail -f logs/bot.log | grep "🌍"
```

Você verá:
```
2025-01-15 14:30:45,123 - src.cogs.matches - INFO - 🌍 /partidas: Timezone do servidor = America/Sao_Paulo
2025-01-15 14:30:45,234 - src.utils.embeds - DEBUG - 📍 create_match_embed usando timezone: America/Sao_Paulo
```

### Opção 3: Testar Mudança de Timezone

1. **Configure um novo timezone**:
```
/timezone set America/New_York
```

2. **Use um comando**:
```
/partidas 3
```

3. **Veja nos logs**:
```
🌍 /partidas: Timezone do servidor = America/New_York
```

---

## 🔍 Interpretando os Logs

### Exemplo de Logs Normais

```
[INFO] 🌍 /partidas: Timezone do servidor = America/Sao_Paulo
[DEBUG] 📍 create_match_embed usando timezone: America/Sao_Paulo
[DEBUG] 📍 Horário exibido com timezone correto
```

**O que significa**:
- ✅ Timezone foi buscado com sucesso
- ✅ Embed foi criado com timezone correto
- ✅ Horários serão exibidos em BRT (Brazil Time)

### Exemplo com Timezone Padrão

Se o timezone não for encontrado, verá:
```
[INFO] 🌍 /partidas: Timezone do servidor = America/Sao_Paulo (DEFAULT)
```

**O que significa**:
- ⚠️ Timezone não configurado no banco
- ✅ Usando default (America/Sao_Paulo)
- ✅ Tudo ainda funciona normalmente

### Exemplo com Timezone Customizado

Se você configurou um timezone diferente:
```
[INFO] 🌍 /partidas: Timezone do servidor = Europe/London
[DEBUG] 📍 create_match_embed usando timezone: Europe/London
```

**O que significa**:
- ✅ Timezone customizado está sendo respeitado
- ✅ Todas as horas aparecerão em horário de Londres

---

## 📊 Mapeamento de Timezone

Aqui estão os timezones mais comuns:

| Timezone | Abreviação | Offset | Região |
|----------|-----------|--------|--------|
| `America/Sao_Paulo` | BRT | -03:00 | Brasil |
| `America/New_York` | EST/EDT | -05:00/-04:00 | EUA Leste |
| `America/Los_Angeles` | PST/PDT | -08:00/-07:00 | EUA Oeste |
| `America/Mexico_City` | CST/CDT | -06:00/-05:00 | México |
| `Europe/London` | GMT/BST | +00:00/+01:00 | UK |
| `Europe/Paris` | CET/CEST | +01:00/+02:00 | Central EU |
| `Europe/Moscow` | MSK | +03:00 | Rússia |
| `Asia/Tokyo` | JST | +09:00 | Japão |
| `Asia/Shanghai` | CST | +08:00 | China |
| `Asia/Singapore` | SGT | +08:00 | Singapura |
| `Australia/Sydney` | AEDT/AEST | +11:00/+10:00 | Austrália |

---

## 🎯 Verificação de Funcionamento

### Checklist Visual

```
✅ Arquivo logs/bot.log criado?
   Depois que você inicia o bot, deve existir um arquivo logs/bot.log

✅ Consegue ver logs?
   tail -f logs/bot.log

✅ Consegue ver timezone sendo usado?
   grep "🌍" logs/bot.log

✅ Timezone muda quando você usa /timezone set?
   Configure /timezone set America/New_York e veja nos logs

✅ Horários aparecem diferentes no Discord?
   Compare timestamps com e sem timezone customizado
```

---

## 🔧 Debugging

### Se não ver os logs

1. **Verificar se logs estão habilitados**:
```bash
# Certificar que arquivo log está sendo criado
ls -la logs/bot.log
```

2. **Verificar level de log**:
```python
# No bot.py, verifique se logging está configurado
# Deve ter: logging.basicConfig(..., level=logging.INFO, ...)
```

3. **Tail do arquivo**:
```bash
# Ver logs em tempo real
tail -100 logs/bot.log  # Últimas 100 linhas
tail -f logs/bot.log     # Seguir logs em tempo real
```

### Se timezone não está sendo usado

1. **Verificar se timezone foi configurado**:
```
/timezone get
```

Deve mostrar o timezone configurado. Se mostrar "não configurado", use:
```
/timezone set America/Sao_Paulo
```

2. **Verificar database**:
```bash
# Verificar se timezone está no banco
python scripts/check_cache_content.py
```

3. **Ver logs de erro**:
```bash
grep "ERROR\|ERRO" logs/bot.log
```

---

## 📝 Exemplo Completo de Logs

Aqui está um exemplo completo do que você verá quando usar `/partidas`:

```
2025-01-15 14:30:42,123 - src.cogs.matches - INFO - 🌍 /partidas: Timezone do servidor = America/Sao_Paulo
2025-01-15 14:30:42,234 - src.utils.embeds - DEBUG - 📍 create_match_embed usando timezone: America/Sao_Paulo
2025-01-15 14:30:42,345 - src.utils.embeds - DEBUG - 📍 create_match_embed usando timezone: America/Sao_Paulo
2025-01-15 14:30:42,456 - src.utils.embeds - DEBUG - 📍 create_match_embed usando timezone: America/Sao_Paulo
2025-01-15 14:30:42,567 - src.cogs.matches - INFO - ✓ Comando /partidas executado por User#0000 (3 partidas do cache)
```

**Interpretação**:
- ✅ Timezone do servidor: `America/Sao_Paulo`
- ✅ 3 embeds criados com timezone correto
- ✅ Comando executado com sucesso

---

## 🚀 Próximos Passos

1. **Inicie o bot**: `venv/bin/python -m src.bot`
2. **Use um comando**: `/partidas 5`
3. **Verifique o log**: `grep "🌍" logs/bot.log`
4. **Veja o timezone**: Procure por `Timezone do servidor = `

Pronto! Agora você consegue ver exatamente qual timezone está sendo respeitado em cada comando! 🎉

---

**Adicionado em**: Phase 2 Timezone Integration  
**Status**: Ready for Testing ✅
