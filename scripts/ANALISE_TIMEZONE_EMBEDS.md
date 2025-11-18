# 🕐 Análise: Timezone + Embeds do Discord

## 📊 Resumo Executivo

Você tem uma lógica robusta de timezone já implementada (`TimezoneManager`), mas os **embeds do Discord estão usando `datetime.utcnow()`** sem conversão para o timezone do usuário/servidor. 

**Problema**: O timestamp que aparece no rodapé dos embeds será sempre UTC, ignorando a configuração de timezone do servidor.

**Solução**: Integrar o `TimezoneManager` com a criação dos embeds para usar `datetime.now(tz)` em vez de `datetime.utcnow()`.

---

## 🔍 Análise da Situação Atual

### 1. **TimezoneManager** (Já implementado ✅)

Localização: `src/utils/timezone_manager.py`

**Capacidades**:
- ✅ Converte UTC → Timezone local (`convert_utc_to_timezone()`)
- ✅ Formata datetime com timezone (`format_datetime_for_display()`)
- ✅ Obtém abreviação do timezone (`get_timezone_abbreviation()`)
- ✅ Obtém offset UTC (`get_timezone_offset()`)
- ✅ Suporta múltiplos timezones via pytz

**Exemplo de uso**:
```python
from src.utils.timezone_manager import TimezoneManager

# Converter UTC para São Paulo
dt_utc = datetime.utcnow()
dt_sp = TimezoneManager.convert_utc_to_timezone(dt_utc, "America/Sao_Paulo")
print(dt_sp)  # 2025-11-18 12:00:00-03:00 (com timezone info)
```

### 2. **Embeds do Discord** (Problema atual ❌)

Localização: `src/utils/embeds.py` (linhas 663, 935, 1245, 1265)

**Situação problemática**:
```python
embed = nextcord.Embed(
    title=f"{emoji} {team1_name} vs {team2_name}",
    color=color,
    timestamp=datetime.utcnow()  # ❌ Sempre UTC!
)
```

**Problema**:
- `datetime.utcnow()` retorna datetime **sem timezone info** (naive)
- Discord mostra o timestamp no **rodapé do embed** em UTC sempre
- Ignora completamente a configuração de timezone do servidor/usuário

**Como Discord interpreta timestamps**:
- Se receber `datetime` **naive** (sem tzinfo): Assume UTC
- Se receber `datetime` **aware** (com tzinfo): Converte para timezone do cliente Discord

---

## 📚 Documentação Nextcord sobre Timestamps

De acordo com a documentação oficial:

### ✅ Forma Correta:
```python
from datetime import datetime, timezone
import nextcord

# Com timezone-aware datetime (recomendado)
embed = nextcord.Embed(
    title="My Embed",
    timestamp=datetime.now(timezone.utc)  # ✅ Aware datetime
)
```

### ❌ Forma Atual (Problemática):
```python
from datetime import datetime
import nextcord

# Sem timezone info (naive)
embed = nextcord.Embed(
    title="My Embed", 
    timestamp=datetime.utcnow()  # ❌ Naive datetime = sempre UTC
)
```

---

## 🎯 Arquitetura da Solução

### **Componentes**:

1. **TimezoneManager** (já existe)
   - Converte entre UTC e timezones locais
   - Gerencia qual timezone usar por servidor/usuário

2. **Create*Embed functions** (modificar)
   - Receber `timezone` como parâmetro
   - Usar `TimezoneManager` para converter `datetime.utcnow()`
   - Passar datetime **com timezone info** para o embed

3. **Caller code** (cogs, commands)
   - Obter timezone do servidor/usuário
   - Passar para as funções de embed

---

## 💡 Opções de Integração

### **Opção 1: Usar Timezone Actual (Discord renderiza localmente)**

**Conceito**: Enviar o horário UTC com timezone info. Discord renderiza no timezone do **cliente** (cada usuário vê no seu timezone).

```python
import nextcord
from datetime import datetime, timezone as dt_timezone

embed = nextcord.Embed(
    title="Match",
    timestamp=datetime.now(dt_timezone.utc)  # ✅ Discord converte para cada cliente
)
```

**Vantagem**:
- Cada usuário vê no seu próprio timezone automaticamente
- Sem necessidade de configuração por servidor

**Desvantagem**:
- Não mostra qual timezone é usado (pode confundir)

---

### **Opção 2: Usar Timezone do Servidor (Recomendado para seu caso)**

**Conceito**: Converter para o timezone configurado do servidor, depois enviar como aware datetime.

```python
import nextcord
from datetime import datetime
import pytz
from src.utils.timezone_manager import TimezoneManager

# Dentro de create_match_embed()
def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    # Obter hora atual no timezone do servidor
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)  # ✅ Com timezone info
    
    embed = nextcord.Embed(
        title="Match",
        color=color,
        timestamp=now_local  # ✅ Embed mostra hora no timezone do servidor
    )
    
    return embed
```

**Vantagem**:
- Embed mostra horário no timezone configurado do servidor
- Consistente com outros campos que já mostram timezone
- Claro para o usuário qual timezone está sendo usado

**Desvantagem**:
- Requer que o timezone seja passado para a função

---

### **Opção 3: Híbrida (Melhor UX)**

**Conceito**: Enviar com timezone do servidor, E adicionar footer explicando o timezone.

```python
import nextcord
from datetime import datetime
import pytz
from src.utils.timezone_manager import TimezoneManager

def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    # Hora atual no timezone do servidor
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    # Obter abreviação do timezone
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
    
    embed = nextcord.Embed(
        title="Match",
        color=color,
        timestamp=now_local
    )
    
    # Footer mostra qual timezone está sendo usado
    footer_text = f"Match ID: {match_id} • {tz_abbr}"
    embed.set_footer(text=footer_text)
    
    return embed
```

**Vantagem**:
- ✅ Mostra timezone no footer
- ✅ Consistent com hora do servidor
- ✅ Claro para o usuário
- ✅ Reutiliza `TimezoneManager`

---

## 🔧 Implementação Proposta

### **Passo 1: Modificar `create_match_embed()`**

```python
import pytz
from datetime import datetime
from src.utils.timezone_manager import TimezoneManager

def create_match_embed(match_data: Dict, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Args:
        match_data: Dados da partida
        timezone: Timezone do servidor (ex: "America/Sao_Paulo")
    """
    # ✅ NOVO: Usar datetime com timezone awareness
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)  # Em vez de datetime.utcnow()
    
    embed = nextcord.Embed(
        title=f"{emoji} {team1_name} vs {team2_name}",
        color=color,
        timestamp=now_local  # ✅ Com timezone info
    )
    
    # ... resto do código ...
    
    # ✅ NOVO: Footer com timezone
    tz_abbr = TimezoneManager.get_timezone_abbreviation(timezone)
    footer_text = f"Match ID: {match_id} • PandaScore API • {tz_abbr}"
    embed.set_footer(text=footer_text)
    
    return embed
```

### **Passo 2: Modificar `create_result_embed()`**

Mesmo padrão que `create_match_embed()`.

### **Passo 3: Modificar `create_error_embed()` e `create_info_embed()`**

```python
def create_error_embed(title: str, description: str, timezone: str = "America/Sao_Paulo") -> nextcord.Embed:
    """
    Args:
        title: Título do erro
        description: Descrição
        timezone: Timezone do servidor
    """
    tz = pytz.timezone(timezone)
    now_local = datetime.now(tz)
    
    embed = nextcord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c,
        timestamp=now_local  # ✅ Com timezone
    )
    
    return embed
```

### **Passo 4: Atualizar chamadas das funções**

Em `src/cogs/matches.py`:

```python
# Antes:
embed = create_match_embed(match_data)

# Depois:
timezone = await self.bot.cache_manager.get_guild_timezone(interaction.guild_id)
embed = create_match_embed(match_data, timezone)
```

---

## 📋 Checklist de Implementação

- [ ] Modificar `create_match_embed()` para aceitar `timezone` e usar `datetime.now(tz)`
- [ ] Modificar `create_result_embed()` com mesmo padrão
- [ ] Modificar `create_error_embed()` e `create_info_embed()` 
- [ ] Atualizar `add_automated_stream_info()` se houver timestamp
- [ ] Atualizar todas as chamadas em `src/cogs/` para passar `timezone`
- [ ] Adicionar footer com `{tz_abbr}` em todos os embeds
- [ ] Testar em um servidor com different timezone
- [ ] Validar que Discord renderiza timestamp corretamente

---

## 🧪 Como Testar

### Teste 1: Verificar timestamp do embed
1. Executar comando `/partidas`
2. Ver rodapé do embed
3. Confirmar que mostra hora no timezone correto

### Teste 2: Comparar com hora do servidor
1. Executar `/timezone-info` para ver timezone do servidor
2. Comparar com timestamp do embed
3. Devem estar alinhados

### Teste 3: Testar com múltiplos timezones
1. Criar servidor de teste com timezone "America/Sao_Paulo"
2. Criar outro com "Europe/London"
3. Executar mesmo comando em ambos
4. Verificar se timestamps são diferentes

---

## 🎓 Resumo Técnico

| Aspecto | Antes (❌) | Depois (✅) |
|--------|-----------|-----------|
| **Função** | `datetime.utcnow()` | `datetime.now(tz)` |
| **Tipo** | Naive (sem tzinfo) | Aware (com tzinfo) |
| **Timezone** | Sempre UTC | Configurável por servidor |
| **Discord renderiza** | UTC para todos | Timezone do servidor |
| **Footer** | Sem info | Com abreviação (BRT, EST, etc) |
| **Experiência** | Confusa | Clara |

---

## 📚 Referências

- **TimezoneManager**: `src/utils/timezone_manager.py`
- **Embeds**: `src/utils/embeds.py` (linhas 663, 935, 1245, 1265)
- **Nextcord Docs**: Timestamp com `datetime.now(timezone.utc)` ou timezone-aware datetimes
- **pytz**: `pytz.timezone(name)` para criar objetos timezone

