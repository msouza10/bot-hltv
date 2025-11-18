# API PandaScore: Streams List e Tier - Especificação Completa

**Data**: 18 de Novembro de 2025  
**Fonte**: Documentação Oficial PandaScore API

---

## 🎬 Streams List - Array de Objects

Campo: `streams_list` (array of objects, required)

Cada objeto de stream contém:

### embed_url (uri | null, required)
URL para embutir em um iframe.

```json
{
  "embed_url": "https://player.kick.com/cct_cs2"
}
```

### language (string enum, required)
Código de idioma em ISO 639-1 (2 caracteres).

Valores possíveis (125+ idiomas):
```
aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs 
ca ce ch co cr cs cu cv cy da de dv dz ee el en eo es et eu fa ff 
fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id 
ie ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku 
kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my 
na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu 
rm rn ro ru rw sa sc sd se sg si sk sl sm sn so sq sr ss st su sv 
sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo 
wa wo xh yi yo za zh zu
```

Exemplos comuns:
```
en → English (Inglês)
pt → Portuguese (Português)
pt-BR → Brazilian Portuguese (Português Brasileiro)
ru → Russian (Russo)
de → German (Alemão)
fr → French (Francês)
es → Spanish (Espanhol)
ja → Japanese (Japonês)
ko → Korean (Coreano)
zh → Chinese (Chinês)
```

### main (boolean, required)
Se é o stream principal. Main stream é sempre official.

```json
{
  "main": true
}
```

### official (boolean, required)
Se é um broadcast oficial.

```json
{
  "official": true
}
```

### raw_url (uri, required)
URL para o stream no site da plataforma.

```json
{
  "raw_url": "https://kick.com/cct_cs2"
}
```

---

## 🏆 Tier - Ranking de Campeonato

Campo: `tournament.tier` (string | null, enum, required)

Valores possíveis (6 valores + null):
```
a b c d s unranked
```

Ranking: **S > A > B > C > D > Unranked**

### Mapping Completo

| Valor | Emoji | Label | Significado |
|-------|-------|-------|-------------|
| **s** | 🏆 | Tier S - Elite | Major/Internacional (Top) |
| **a** | 👑 | Tier A - Top | Internacional/Premium |
| **b** | 🥇 | Tier B - Profissional | Profissional Regional |
| **c** | 🥈 | Tier C - Semi-Pro | Semi-profissional |
| **d** | 🥉 | Tier D - Regional | Regional/Amador |
| **unranked** | ❓ | Unranked | Sem classificação |
| **null** | ❓ | Desconhecido | Dados faltando |

---

## 📝 Exemplos de Resposta Completa

### Stream Object Exemplo

```json
{
  "main": true,
  "language": "en",
  "embed_url": "https://player.kick.com/cct_cs2",
  "official": true,
  "raw_url": "https://kick.com/cct_cs2"
}
```

### Tournament com Tier

```json
{
  "tournament": {
    "id": 18006,
    "name": "Playoffs",
    "type": "online",
    "tier": "d",
    "region": "EEU"
  }
}
```

---

## 🔧 Implementação em Código

### Mapeamento de Tier

```python
TIER_MAP = {
    "s": {"emoji": "🏆", "label": "Tier S - Elite"},
    "a": {"emoji": "👑", "label": "Tier A - Top"},
    "b": {"emoji": "🥇", "label": "Tier B - Profissional"},
    "c": {"emoji": "🥈", "label": "Tier C - Semi-Pro"},
    "d": {"emoji": "🥉", "label": "Tier D - Regional"},
    "unranked": {"emoji": "❓", "label": "Unranked"},
}
```

### Mapeamento de Linguagem

```python
LANGUAGE_FLAGS = {
    "en": "🇬🇧",
    "pt": "🇧🇷",
    "pt-BR": "🇧🇷",
    "ru": "🇷🇺",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "zh": "🇨🇳",
    # ... mais idiomas
}
```

---

## 📂 Arquivos de Referência

- **Implementação**: `src/utils/embeds.py`
  - Mapas: `TIER_MAP`, `LANGUAGE_FLAGS`
  - Funções: `get_tier_info()`, `format_streams_field()`

- **Testes**: `scripts/test_tournament_info.py`
  - Testa todos os 6 tiers + unranked + null
  - Resultado: ✅ TESTE CONCLUÍDO COM SUCESSO

- **Documentação**:
  - `docs/ANALISE_TIER_NACIONALIDADE.md`
  - `docs/QUICK_REF_REGIONS.md`

---

## 📊 Casos de Uso

### Exemplo 1: Major (Tier S)
```
Tournament Tier: S
Main Stream: en (Inglês)
Official: true
URL: https://twitch.tv/esl_csgo
```

### Exemplo 2: Regional (Tier D)
```
Tournament Tier: D
Main Stream: pt-BR (Português Brasileiro)
Official: false
URL: https://twitch.tv/cct_cs2
```

### Exemplo 3: Semi-Pro (Tier C)
```
Tournament Tier: C
Streams: [
  { language: "en", official: true, main: true },
  { language: "ru", official: false, main: false },
  { language: "pt", official: false, main: false }
]
```

---

## ⚠️ Considerações

- **Tier pode ser null**: Verificar antes de usar
- **Language é ISO 639-1**: 2 caracteres minúsculos
- **Main stream**: Sempre priorizar se disponível
- **Official**: Não garante qualidade, apenas que é broadcast oficial
- **Embed_url pode ser null**: Usar raw_url como fallback

---

## 🧪 Teste

```bash
python scripts/test_tournament_info.py
```

Output esperado:
```
🎯 TESTE 1: Tier (get_tier_info)
  s          → 🏆 Tier S - Elite
  a          → 👑 Tier A - Top
  b          → 🥇 Tier B - Profissional
  c          → 🥈 Tier C - Semi-Pro
  d          → 🥉 Tier D - Regional
  unranked   → ❓ Unranked
  unknown    → ❓ Tier Desconhecido
  None       → ❓ Tier Desconhecido
```

---

## ✅ Status

Implementação: **Completa e Testada**
- ✅ Suporte para 6 tiers + unranked + null
- ✅ 125+ idiomas suportados na API
- ✅ Formatação de streams com idiomas
- ✅ Testes passando
