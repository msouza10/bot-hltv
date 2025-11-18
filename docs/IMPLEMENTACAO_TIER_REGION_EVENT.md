# 🎯 Implementação: Tier, Region e Event Type nos Embeds

**Data**: 18 de Novembro de 2025  
**Status**: ✅ Implementado e Testado

---

## 📋 Resumo Executivo

Adicionado informações de **Tier do Campeonato**, **Região Geográfica** e **Tipo de Evento** aos embeds do Discord.

Os dados já eram capturados pela API e cacheados, mas **não eram exibidos** nos embeds. Agora são mostrados em um novo campo chamado **"🎯 Detalhes do Campeonato"**.

---

## 🔄 Fluxo de Dados

```
PandaScore API
├─ tournament.tier       (d, c, b, a, s)
├─ tournament.region     (EEU, WEU, NA, SA, OCE, AS)
└─ tournament.type       (online, offline, online-and-offline)
         ↓
cache_manager.py
├─ Armazena tudo como JSON em matches_cache
└─ Campo: match_data (todo o objeto preservado)
         ↓
embeds.py (NEW! ✨)
├─ Extrai tournament.tier
├─ Extrai tournament.region
├─ Extrai tournament.type
├─ Formata com emojis e labels
└─ Exibe em "🎯 Detalhes do Campeonato"
         ↓
Discord Embed
└─ Mostra ao usuário: Tier + Região + Tipo de Evento
```

---

## 📝 O Que Foi Implementado

### 1️⃣ Funções Auxiliares em `src/utils/embeds.py`

Adicionadas 3 novas funções e 3 mapas de dados:

#### TIER_MAP - Mapeia tiers para emoji e label

```python
{
    "s": {"emoji": "🏆", "label": "Tier S - Elite"},
    "a": {"emoji": "👑", "label": "Tier A - Top"},
    "b": {"emoji": "🥇", "label": "Tier B - Profissional"},
    "c": {"emoji": "🥈", "label": "Tier C - Semi-Pro"},
    "d": {"emoji": "🥉", "label": "Tier D - Regional"},
}
```

#### REGION_MAP - Mapeia regiões para emoji e label

```python
{
    "EEU": {"emoji": "🇪🇺", "label": "Leste Europeu"},
    "WEU": {"emoji": "🇪🇺", "label": "Oeste Europeu"},
    "NA": {"emoji": "🇺🇸", "label": "América do Norte"},
    "SA": {"emoji": "🇧🇷", "label": "América do Sul"},
    "OCE": {"emoji": "🇦🇺", "label": "Oceania"},
    "AS": {"emoji": "🌏", "label": "Ásia"},
}
```

#### EVENT_TYPE_MAP - Mapeia tipo de evento para emoji

```python
{
    "online": "💻",
    "offline": "🏟️",
    "online-and-offline": "🌐",
}
```

#### get_tier_info(tier: str) → (emoji, label)

Converte código de tier para emoji + label formatado.

#### get_region_info(region: str) → (emoji, label)

Converte código de região para emoji + label formatado.

#### get_event_type_info(event_type: str) → (emoji, label)
Converte tipo de evento para emoji + label formatado.

### 2️⃣ Adicionado Novo Campo "🎯 Detalhes do Campeonato"

**Em `create_match_embed()`:**
```python
tournament_info = f"{tier_emoji} {tier_label}\n{region_emoji} {region_label}\n{event_emoji} {event_label}"

embed.add_field(
    name="🎯 Detalhes do Campeonato",
    value=tournament_info,
    inline=False
)
```

**Em `create_result_embed()`:**
```python
tournament_details = f"{tier_emoji} {tier_label}\n{region_emoji} {region_label}\n{event_emoji} {event_label}"

embed.add_field(
    name="🎯 Detalhes do Campeonato",
    value=tournament_details,
    inline=False
)
```

---

## 💾 Cache - Sem Mudanças Necessárias

Os dados **já estavam sendo cacheados** em `cache_manager.py`:

```python
match_data = json.dumps(match)  # ← Preserva tournament.tier, tournament.region, tournament.type
# ... inserir em BD ...
```

O campo `match_data` armazena o **JSON completo** do match, incluindo todo o objeto `tournament`. Portanto, **nenhuma alteração foi necessária** no cache.

---

## 📊 Exemplos de Saída

### Exemplo 1: Partida CCT Europe (Tier D, Leste Europeu, Online)

```
🎯 Detalhes do Campeonato
🥉 Tier D - Regional
🇪🇺 Leste Europeu
💻 Online
```

### Exemplo 2: Major (Tier S, Europa Ocidental, Online)

```
🎯 Detalhes do Campeonato
🏆 Tier S - Elite
🇪🇺 Oeste Europeu
💻 Online
```

### Exemplo 3: Offline LAN (Tier A, América do Norte)

```
🎯 Detalhes do Campeonato
👑 Tier A - Top
🇺🇸 América do Norte
🏟️ Offline
```

---

## 🧪 Teste Implementado

Script criado: `scripts/test_tournament_info.py`

**O que testa:**
- ✅ Função `get_tier_info()` com todos os tiers
- ✅ Função `get_region_info()` com todas as regiões
- ✅ Função `get_event_type_info()` com todos os tipos
- ✅ Comportamento com valores `None` ou desconhecidos
- ✅ Estrutura de um match JSON real

**Resultado:**
```
✅ TESTE CONCLUÍDO COM SUCESSO!
```

---

## 🚀 Como Usar

### 1. Iniciar o Bot
```bash
python -m src.bot
```

### 2. Usar os Comandos Discord
- `/partidas` - Ver próximas partidas
- `/aovivo` - Ver partidas em andamento
- `/resultados` - Ver resultados finalizados

### 3. Verificar os Novos Campos
Procure pelo campo **"🎯 Detalhes do Campeonato"** em qualquer embed de partida.

---

## 📁 Arquivos Modificados

### Modificados:
- **`src/utils/embeds.py`**
  - Adicionadas 3 mapas: `TIER_MAP`, `REGION_MAP`, `EVENT_TYPE_MAP`
  - Adicionadas 3 funções: `get_tier_info()`, `get_region_info()`, `get_event_type_info()`
  - Campo "🎯 Detalhes do Campeonato" em `create_match_embed()`
  - Campo "🎯 Detalhes do Campeonato" em `create_result_embed()`

### Criados:
- **`scripts/test_tournament_info.py`** - Script de teste

### Não Modificados:
- `src/database/cache_manager.py` - Cache já estava completo
- `src/database/schema.sql` - BD schema já suporta
- Todos os cogs e serviços - Funcionam transparentemente

---

## 💡 Comportamento com Dados Faltantes

Cada função trata gracefully valores `None` ou desconhecidos:

```python
# Se tier for None
get_tier_info(None)  
→ ("❓", "Tier Desconhecido")

# Se region for "FOO" (desconhecido)
get_region_info("FOO")  
→ ("🌍", "Regional")

# Se type for None
get_event_type_info(None)  
→ ("❓", "Tipo Desconhecido")
```

---

## 📚 Documentação Relacionada

Veja também:
- `docs/ANALISE_TIER_NACIONALIDADE.md` - Análise completa dos campos de tier, region e nationality
- `docs/ANALISE_ESTRUTURA_API_PANDASCORE.md` - Referência completa de estrutura da API

---

## ✅ Checklist de Implementação

- [x] Analisar dados de tier, region e type na API
- [x] Criar mapas de emojis e labels
- [x] Implementar funções de formatação
- [x] Adicionar campo em `create_match_embed()`
- [x] Adicionar campo em `create_result_embed()`
- [x] Testar com valores válidos
- [x] Testar com valores None/desconhecidos
- [x] Criar script de teste
- [x] Documentar implementação
- [x] Verificar sem erros de código

---

## 🎯 Próximos Passos (Opcional)

1. **Adicionar Core Web Vitals**
   - Performance de embeds renderizados
   - Verificar tamanho do campo no Discord

2. **Cacheamento de Formatação**
   - Se houver muitos matches, cachear strings formatadas
   - Reduz cálculo em tempo de execução

3. **Customização por Guild**
   - Permitir que servidores escolham quais detalhes mostrar
   - Salvar preferências em `guild_config`

4. **Filtros por Tier/Região**
   - Permitir `/partidas tier:s` ou `/partidas region:EEU`
   - Seria uma ótima feature!

---

## 📞 Suporte

Se houver algum problema:

1. Verifique os logs em `logs/bot.log`
2. Execute `python scripts/test_tournament_info.py`
3. Confirme que API está retornando dados com `tournament.tier`, `tournament.region`, `tournament.type`
