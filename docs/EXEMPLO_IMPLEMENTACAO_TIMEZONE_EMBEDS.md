# 🛠️ Exemplo Prático: Integração Timezone + Embeds

Este arquivo mostra exemplos práticos de como modificar o código.

## 1️⃣ Modificação em `create_match_embed()`

### ❌ ANTES:
```python
def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    import logging
    logger = logging.getLogger(__name__)
    
    # ... código ...
    
    # Criar embed
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=datetime.utcnow()  # ❌ PROBLEMA: Sempre UTC, sem timezone info
    )
    
    # ... resto ...
```

### ✅ DEPOIS:
```python
def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    import logging
    import pytz  # ✅ NOVO
    
    logger = logging.getLogger(__name__)
    logger.debug(f"📍 create_match_embed usando timezone: {timezone}")
    
    # ... código ...
    
    # ✅ NOVO: Criar datetime com timezone awareness
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)  # Em vez de datetime.utcnow()
    
    # Criar embed
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=now_local  # ✅ Com timezone info
    )
    
    # ... resto do código ...
    
    # ✅ MODIFICADO: Footer agora mostra timezone
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr}"
    embed.set_footer(text=footer_text)
    
    return embed
```

---

## 2️⃣ Modificação em `create_result_embed()`

### ✅ PADRÃO (mesmo de create_match_embed):
```python
def create_result_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    import logging
    import pytz  # ✅ NOVO
    
    logger = logging.getLogger(__name__)
    logger.debug(f"📍 create_result_embed usando timezone: {timezone}")
    
    # ... código ...
    
    # ✅ NOVO: Criar datetime com timezone awareness
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    # Embed
    embed = nextcord.Embed(
        color=color,
        timestamp=now_local  # ✅ Com timezone info
    )
    
    # ... resto do código ...
    
    # ✅ MODIFICADO: Footer com timezone
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr}"
    embed.set_footer(text=footer_text)
    
    return embed
```

---

## 3️⃣ Modificação em `create_error_embed()` e `create_info_embed()`

### ❌ ANTES:
```python
def create_error_embed(title: str, description: str) -> nextcord.Embed:
    embed = nextcord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c,
        timestamp=datetime.utcnow()  # ❌ Sempre UTC
    )
    return embed
```

### ✅ DEPOIS:
```python
def create_error_embed(title: str, description: str, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Args:
        title: Título do erro
        description: Descrição do erro
        timezone: Timezone do servidor (default: "America/Sao_Paulo")
    """
    import pytz  # ✅ NOVO
    
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    embed = nextcord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c,
        timestamp=now_local  # ✅ Com timezone info
    )
    return embed
```

### ✅ MESMO PARA create_info_embed():
```python
def create_info_embed(title: str, description: str, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Args:
        title: Título
        description: Descrição
        timezone: Timezone do servidor
    """
    import pytz  # ✅ NOVO
    
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    embed = nextcord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=0x3498db,
        timestamp=now_local  # ✅ Com timezone info
    )
    return embed
```

---

## 4️⃣ Como Atualizar Chamadas nos COGS

### Em `src/cogs/matches.py`:

#### ❌ ANTES:
```python
@nextcord.slash_command(name="partidas", description="Ver próximas partidas")
async def partidas(self, interaction: nextcord.Interaction, quantidade: int = 5):
    matches = await self.bot.cache_manager.get_cached_matches("upcoming", quantidade)
    
    embeds = []
    for match in matches:
        embed = create_match_embed(match)  # ❌ Sem timezone
        embeds.append(embed)
    
    await interaction.response.send_message(embeds=embeds)
```

#### ✅ DEPOIS:
```python
@nextcord.slash_command(name="partidas", description="Ver próximas partidas")
async def partidas(self, interaction: nextcord.Interaction, quantidade: int = 5):
    # ✅ NOVO: Obter timezone do servidor
    timezone = await self.bot.cache_manager.get_guild_timezone(interaction.guild_id)
    
    matches = await self.bot.cache_manager.get_cached_matches("upcoming", quantidade)
    
    embeds = []
    for match in matches:
        embed = create_match_embed(match, timezone)  # ✅ Com timezone
        embeds.append(embed)
    
    await interaction.response.send_message(embeds=embeds)
```

---

## 5️⃣ Padrão para Todos os Comandos

Use este padrão em **todos os slash commands** que usam embeds:

```python
@nextcord.slash_command(name="seu_comando", description="Descrição")
async def seu_comando(self, interaction: nextcord.Interaction):
    # ✅ PASSO 1: Obter timezone do servidor
    timezone = await self.bot.cache_manager.get_guild_timezone(interaction.guild_id)
    
    # PASSO 2: Obter dados
    dados = await self.bot.cache_manager.get_cached_matches(...)
    
    # PASSO 3: Criar embed COM timezone
    embed = create_match_embed(dados, timezone)
    
    # PASSO 4: Enviar
    await interaction.response.send_message(embed=embed)
```

---

## 6️⃣ Testes Manuais

### Teste 1: Verificar que timestamp está com timezone
```bash
# No seu bot de teste:
# 1. Execute /partidas
# 2. Veja o embed
# 3. No rodapé deve mostrar algo como:
#    "Match ID: 12345 • PandaScore API • BRT"
#    
# "BRT" = Brazil Time (em vez de apenas UTC)
```

### Teste 2: Comparar com /timezone-info
```bash
# Se tiver comando /timezone-info
# 1. Execute /timezone-info
# 2. Compare o timezone mostrado
# 3. Verifique se bate com o abreviado no embed (BRT, EST, CET, etc)
```

### Teste 3: Testar com erro
```bash
# 1. Trigger algum erro (comando inválido, etc)
# 2. Veja se o error embed também mostra o timezone correto
```

---

## 7️⃣ Checklist de Arquivos a Modificar

- [ ] `src/utils/embeds.py` - Adicionar `import pytz` no topo
- [ ] `src/utils/embeds.py` - Modificar `create_match_embed()`
- [ ] `src/utils/embeds.py` - Modificar `create_result_embed()`
- [ ] `src/utils/embeds.py` - Modificar `create_error_embed()`
- [ ] `src/utils/embeds.py` - Modificar `create_info_embed()`
- [ ] `src/utils/embeds.py` - Modificar `add_automated_stream_info()` (se houver timestamp)
- [ ] `src/cogs/matches.py` - Adicionar `timezone = await self.bot.cache_manager.get_guild_timezone()`
- [ ] `src/cogs/notifications.py` - Mesmo padrão
- [ ] `src/cogs/ping.py` - Mesmo padrão

---

## 8️⃣ Validação Técnica

```python
# Isto é o que Discord espera receber:

import pytz
from datetime import datetime

# ✅ CORRETO (timezone-aware):
tz = pytz.timezone("America/Sao_Paulo")
now_aware = datetime.now(tz)
print(now_aware)  # 2025-11-18 12:00:00-03:00
print(now_aware.tzinfo)  # UTC-03:00 (com timezone info)

# ❌ INCORRETO (naive):
now_naive = datetime.utcnow()
print(now_naive)  # 2025-11-18 15:00:00
print(now_naive.tzinfo)  # None (SEM timezone info)

# Discord renderiza diferente:
# - datetime aware (✅): Mostra no timezone correto
# - datetime naive (❌): Sempre assume UTC
```

---

## 9️⃣ Exemplo Completo de Uma Função Convertida

```python
def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Cria um embed formatado para exibir informações de uma partida.
    
    ✨ NOVO: Timezone-aware timestamp
    
    Args:
        match_data: Dados da partida retornados pela PandaScore API
        timezone: Timezone para exibição de horários (default: America/Sao_Paulo)
        
    Returns:
        Embed do Discord formatado com timestamp no timezone do servidor
    """
    import logging
    import pytz  # ✅ NOVO
    
    logger = logging.getLogger(__name__)
    logger.debug(f"📍 create_match_embed usando timezone: {timezone}")
    
    # ... resto do código original ...
    
    # ✅ NOVO: Timestamp com timezone awareness
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    # Criar embed
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=now_local  # ✅ Com timezone info
    )
    
    # ... campo de torneio, série, etc ...
    
    # ✅ MODIFICADO: Footer com timezone
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr}"
    embed.set_footer(text=footer_text)
    
    return embed
```

---

## 🎯 Resumo

| Item | Antes | Depois |
|------|-------|--------|
| Import | `from datetime import datetime` | + `import pytz` |
| Timestamp | `datetime.utcnow()` | `datetime.now(tz)` |
| Timezone info | Nenhuma | Através de `pytz.timezone()` |
| Footer | "Match ID: 123 • API" | "Match ID: 123 • API • BRT" |
| Experiência | UTC sempre | Timezone do servidor |

Todos os exemplos acima podem ser implementados diretamente no seu código!

