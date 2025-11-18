# 🕐 Estratégia de Timezone para Bot HLTV

**Data**: Novembro 18, 2025  
**Status**: Em Implementação  
**Objetivo**: Exibir horários corretos em todos os fusos horários, com dados permanecendo em UTC

---

## 📋 Problema Original

Usuários em diferentes fusos horários viam horários incorretos:

```
Exemplo: Jogo às 10:00 da manhã (Brasil, UTC-3)

Hoje (Brasileiro):
❌ Aparecia em plena madrugada (como 13:00 UTC)
❌ Confusão com horários de partidas
❌ Trocas de channel com outras regiões não funcionavam
```

---

## ✅ Solução Implementada

### Princípios Fundamentais

1. **Dados no Banco = UTC Sempre**
   - Nenhuma mudança nos dados existentes
   - `begin_at`, `scheduled_at`, `end_at` continuam em UTC
   - Conversão acontece APENAS na exibição (embeds, mensagens)

2. **Timezone por Servidor**
   - Cada guild Discord tem seu próprio timezone
   - Padrão: `America/Sao_Paulo` (Brasil)
   - Usuários podem override com `/timezone`

3. **Exibição Dinâmica**
   - Horários convertidos no momento de criar embeds
   - Cada servidor vê horários no seu fuso
   - Reminders e notificações respeitam timezone

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    PandaScore API                            │
│               (timestamps em UTC)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              libSQL Database (UTC)                           │
│                                                              │
│  matches_cache:                                              │
│  ├─ begin_at: 2025-11-18T15:00:00Z  (UTC)                   │
│  ├─ scheduled_at: 2025-11-18T15:00:00Z  (UTC)               │
│  └─ end_at: 2025-11-18T16:30:00Z  (UTC)                     │
│                                                              │
│  guild_config:                                               │
│  ├─ guild_id: 1234567890                                    │
│  ├─ timezone: "America/Sao_Paulo"  ✨ NEW                   │
│  └─ notification_channel_id: 9876543210                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          TimezoneManager (Conversão)                        │
│                                                              │
│  convert_utc_to_timezone(dt, "America/Sao_Paulo")           │
│  ├─ 15:00 UTC  ──────→  12:00 BRT (UTC-3)                   │
│  └─ Horário correto para exibição!                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Embeds & Mensagens no Discord                       │
│                                                              │
│  ⏰ Horário: 18/11 12:00 (America/Sao_Paulo - UTC-3)        │
│  ⏰ Horário: 18/11 16:00 (Europe/London - UTC+0)            │
│  ⏰ Horário: 18/11 23:00 (Asia/Tokyo - UTC+9)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Implementação

### 1. Novo Módulo: `src/utils/timezone_manager.py`

**Funções principais:**

```python
# Conversão de datetime
converted = TimezoneManager.convert_utc_to_timezone(
    utc_datetime,
    "America/Sao_Paulo"
)

# Formatação para exibição
formatted = TimezoneManager.format_datetime_for_display(
    utc_datetime,
    "America/Sao_Paulo",
    "%d/%m/%Y %H:%M"
)

# Timestamp Discord (respeta timezone do cliente)
timestamp = TimezoneManager.discord_timestamp(
    utc_datetime,
    "America/Sao_Paulo"
)

# Validação de timezone
is_valid = TimezoneManager.is_valid_timezone("America/Sao_Paulo")

# Informações do timezone
abbr = TimezoneManager.get_timezone_abbreviation("America/Sao_Paulo")  # "BRT"
offset = TimezoneManager.get_timezone_offset("America/Sao_Paulo")     # "UTC-3"
emoji = TimezoneManager.get_server_timezone_emoji("America/Sao_Paulo") # "🇧🇷"
```

**Recursos:**

- ✅ Parse ISO 8601 (formato PandaScore API)
- ✅ Conversão UTC ↔ Timezone
- ✅ Validação de timezone
- ✅ Geração de Discord timestamps
- ✅ Suporte a 400+ timezones (pytz)
- ✅ Abreviações e offsets
- ✅ Emojis representativos

### 2. Banco de Dados: `src/database/schema.sql`

**Nova coluna em `guild_config`:**

```sql
ALTER TABLE guild_config ADD COLUMN timezone TEXT DEFAULT 'America/Sao_Paulo';
```

ou em nova instalação:

```sql
CREATE TABLE guild_config (
    guild_id INTEGER PRIMARY KEY,
    timezone TEXT DEFAULT 'America/Sao_Paulo',  -- ✨ NEW
    ...
);
```

### 3. Comando Discord: `/timezone`

**Implementado em `src/cogs/notifications.py`:**

```
/timezone fuso_horario:"America/Sao_Paulo"
```

**Exemplo de uso:**

```
Usuário Admin: /timezone fuso_horario:America/Sao_Paulo
Bot: ✅ Timezone Configurado - America/Sao_Paulo
     📍 Abreviação: BRT
     📍 Offset: UTC-3
     🌍 Emoji: 🇧🇷
```

**Timezones Suportados:**

```
🇧🇷 Brazil          America/Sao_Paulo
🇺🇸 USA - East      America/New_York
🇺🇸 USA - Chicago   America/Chicago
🇺🇸 USA - West      America/Los_Angeles
🇬🇧 UK              Europe/London
🇫🇷 France          Europe/Paris
🇩🇪 Germany         Europe/Berlin
🇮🇹 Italy           Europe/Rome
🇷🇺 Russia          Europe/Moscow
🇯🇵 Japan           Asia/Tokyo
🇨🇳 China           Asia/Shanghai
🇮🇳 India           Asia/Kolkata
🇦🇺 Australia       Australia/Sydney
```

---

## 🔄 Fluxo Completo

### Cenário 1: Usuário no Brasil
```
1. Admin executa: /timezone America/Sao_Paulo
2. Stored em: guild_config.timezone = "America/Sao_Paulo"
3. Usuário digita: /partidas
4. Bot:
   a. Busca matches do cache (UTC)
   b. Carrega timezone: "America/Sao_Paulo"
   c. Converte: 15:00 UTC → 12:00 BRT
   d. Cria embed com 12:00
   e. Envia para Discord
5. Resultado: ✅ Horário correto no Brasil!
```

### Cenário 2: Mesmo servidor, múltiplos clientes
```
Servidor configurado: /timezone America/Sao_Paulo

💻 Usuário em São Paulo:
   Vê: 12:00 BRT (12:00 local)

💻 Usuário em Londres (mesmo servidor):
   Vê: 15:00 GMT (horário convertido, mas mensagem é em BRT)
   → Usuário localiza: 15:00 = 12:00 + 3 horas
```

### Cenário 3: Múltiplos servidores, mesma partida
```
Partida: 2025-11-18T15:00:00Z (UTC)

Servidor Brasil:  /timezone America/Sao_Paulo
→ Exibe: 18/11 12:00 🇧🇷

Servidor Europe: /timezone Europe/London
→ Exibe: 18/11 15:00 🇬🇧

Servidor Asia:    /timezone Asia/Tokyo
→ Exibe: 19/11 00:00 🇯🇵

✅ Todos corretos!
```

---

## 📝 Atualizações de Código Necessárias

### Prioridade 1: Embeds (Critical Path)

**Arquivo**: `src/utils/embeds.py`

Modificar funções para aceitar timezone:

```python
def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria embed com horários convertidos para timezone.
    """
    from src.utils.timezone_manager import TimezoneManager
    
    # Parse do horário
    time_to_display = match_data.get("scheduled_at") or match_data.get("begin_at")
    
    if time_to_display:
        dt = TimezoneManager.parse_iso_datetime(time_to_display)
        
        # Método 1: Discord timestamp (melhor, respeita cliente)
        timestamp = TimezoneManager.discord_timestamp(dt, timezone)
        
        # Método 2: Formatação manual (alternativa)
        formatted = TimezoneManager.format_datetime_for_display(
            dt, timezone, "%d/%m/%Y %H:%M"
        )
        
        # Usar timestamp Discord (melhor)
        embed.add_field(
            name="⏰ Horário",
            value=f"{timestamp} ({TimezoneManager.get_timezone_abbreviation(timezone)})",
            inline=False
        )
```

### Prioridade 2: Cogs (Comandos)

**Arquivo**: `src/cogs/matches.py`

```python
async def partidas(self, interaction: nextcord.Interaction, quantidade: int = 5):
    """Lista próximas partidas com timezone do servidor."""
    
    # Buscar timezone do servidor
    client = await self.bot.cache_manager.get_client()
    result = await client.execute(
        "SELECT timezone FROM guild_config WHERE guild_id = ?",
        [interaction.guild_id]
    )
    
    timezone = "America/Sao_Paulo"  # default
    if result.rows:
        timezone = result.rows[0][0] or timezone
    
    # Criar embeds com timezone
    for match in matches:
        match = await augment_match_with_streams(match, self.bot.cache_manager)
        embed = create_match_embed(match, timezone)  # ✨ Pass timezone
        embeds.append(embed)
```

### Prioridade 3: Notificações

**Arquivo**: `src/services/notification_manager.py`

```python
async def _create_reminder_embed(self, match_data, timezone):
    """Cria embed de lembrete com timezone."""
    
    # Passar timezone para create_match_embed
    embed = create_match_embed(match_data, timezone)
    return embed
```

---

## 🧪 Testes & Validação

### Script de Teste: `scripts/test_timezone_conversion.py`

```python
async def test_timezone_conversion():
    """
    Testa conversão de timezones.
    """
    from src.utils.timezone_manager import TimezoneManager
    
    # Teste 1: Conversão básica
    dt_utc = TimezoneManager.parse_iso_datetime("2025-11-18T15:00:00Z")
    
    # Brasil
    dt_br = TimezoneManager.convert_utc_to_timezone(dt_br, "America/Sao_Paulo")
    assert dt_br.hour == 12  # 15 - 3 = 12
    
    # Europa
    dt_eu = TimezoneManager.convert_utc_to_timezone(dt_utc, "Europe/London")
    assert dt_eu.hour == 15  # 15 + 0 = 15
    
    # Ásia
    dt_asia = TimezoneManager.convert_utc_to_timezone(dt_utc, "Asia/Tokyo")
    assert dt_asia.hour == 0  # 15 + 9 = 24 → 0 (próximo dia)
    
    print("✅ Testes de timezone passaram!")
```

---

## 🔐 Compatibilidade & Backward Compatibility

### Problemas Potenciais & Soluções

| Problema | Solução |
|----------|---------|
| Banco sem coluna `timezone` | Executar migration ou `build_db.py` novamente |
| Timezone inválido no banco | Fallback para "America/Sao_Paulo" |
| Horários não convertidos em lembretes | Passar timezone em `notification_manager` |
| Discord timestamps diferem por client | ✅ Normal! Cada usuário vê na sua zona |

### Migration Path (se necessário)

```sql
-- Para bancos existentes:
ALTER TABLE guild_config 
ADD COLUMN timezone TEXT DEFAULT 'America/Sao_Paulo';

-- Ou ao criar novo banco (já incluído no schema.sql):
CREATE TABLE guild_config (
    ...
    timezone TEXT DEFAULT 'America/Sao_Paulo',
    ...
);
```

---

## 📊 Exemplos Visuais

### Antes (❌ Errado)
```
Bot em Brasil, partida às 15:00 UTC:

Próximas Partidas de CS2:
┌─────────────────────────────────────────┐
│ Team A vs Team B                         │
│ Torneio: ESL Pro League                  │
│ ⏰ Horário: <t:1742904000:F>             │
│   (15:00 UTC - confuso para brasileiros) │
└─────────────────────────────────────────┘
```

### Depois (✅ Correto)
```
Bot em Brasil, partida às 15:00 UTC:

Próximas Partidas de CS2:
┌─────────────────────────────────────────┐
│ Team A vs Team B                         │
│ Torneio: ESL Pro League                  │
│ ⏰ Horário: <t:1742904000:F> (BRT)       │
│   (18/11 12:00 - claro para brasileiros!)|
│   🇧🇷 America/Sao_Paulo (UTC-3)         │
└─────────────────────────────────────────┘
```

---

## 🚀 Roadmap de Implementação

### Fase 1: Fundação (✅ Completo)
- [x] Módulo `TimezoneManager` com funções de conversão
- [x] Coluna `timezone` no schema
- [x] Comando `/timezone` para configuração
- [x] Validação de timezones

### Fase 2: Embeds (🔄 Em Progresso)
- [ ] Atualizar `create_match_embed()` para usar timezone
- [ ] Atualizar `create_result_embed()` para usar timezone
- [ ] Testar conversões em todos os campos de tempo

### Fase 3: Cogs (📋 Próximo)
- [ ] Atualizar `/partidas` para buscar timezone
- [ ] Atualizar `/aovivo` para usar timezone
- [ ] Atualizar `/resultados` para usar timezone

### Fase 4: Notificações (📋 Próximo)
- [ ] Atualizar `notification_manager` para usar timezone
- [ ] Testar lembretes com timezone
- [ ] Testar notificações de resultado

### Fase 5: Testes & Docs (📋 Final)
- [ ] Script de teste de timezone
- [ ] Documentação completa
- [ ] Testes com múltiplos servidores

---

## 🎯 Benefícios

✅ **Usuarios felizes**: Horários corretos em qualquer fuso  
✅ **Sem breaking changes**: Dados em UTC não mudam  
✅ **Escalável**: Funciona com N servidores  
✅ **Flexível**: Cada servidor escolhe seu timezone  
✅ **Backward compatible**: Fallback para default se não configurado  
✅ **Fácil debug**: Timestamp Discord mostra hora local do usuário  

---

## 📚 Referências

- **pytz Documentation**: https://pypi.org/project/pytz/
- **IANA Timezone Database**: https://www.iana.org/time-zones
- **Discord Timestamps**: https://discord.com/developers/docs/reference#message-formatting
- **ISO 8601**: https://en.wikipedia.org/wiki/ISO_8601

---

**Status**: 🟡 Em Implementação  
**Próximo passo**: Atualizar embeds.py com suporte a timezone
