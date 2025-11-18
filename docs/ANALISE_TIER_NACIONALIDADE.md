# Análise: Tier do Campeonato e Nacionalidade na API PandaScore

**Data**: 18 de Novembro de 2025  
**Status**: Análise Completa  

---

## 📊 Resumo Executivo

| Informação | Disponível? | Local | Notas |
|-----------|-----------|--------|-------|
| **Tier do Campeonato** | ✅ **SIM** | `tournament.tier` | Valores: d, c, b, a, s |
| **Nacionalidade do Campeonato** | ❌ **NÃO** | - | Campo `tournament.country` é sempre `null` para eventos online |
| **Região do Campeonato** | ✅ **SIM** | `tournament.region` | Valores: EEU, WEU, OCE, SA, etc |

---

## 🎯 Tier do Campeonato - DISPONÍVEL ✅

### Campo: `tournament.tier`

O PandaScore **SIM traz** o tier (nível) do campeonato através do campo:

```json
{
  "tournament": {
    "id": 18006,
    "name": "Playoffs",
    "tier": "d",  // ← AQUI ESTÁ O TIER
    "region": "EEU"
  }
}
```

### Valores Possíveis

| Tier | Significado | Exemplo |
|------|-------------|---------|
| **d** | Tier D (mais baixo) | Campeonatos regionais/amadores |
| **c** | Tier C | Campeonatos semi-profissionais |
| **b** | Tier B | Campeonatos profissionais regionais |
| **a** | Tier A | Campeonatos internacionais |
| **s** | Tier S (mais alto) | Majors, eventos de elite |

### Implementação no Código

```python
# Exemplo em cache_manager.py ou embeds.py
tournament_tier = match_data.get("tournament", {}).get("tier", "unknown")

# Mapear para emoji/cor
tier_emoji = {
    "s": "🏆",  # Elite
    "a": "👑",  # Top tier
    "b": "🥇",  # Profissional
    "c": "🥈",  # Semi-pro
    "d": "🥉",  # Regional
    "unknown": "❓"
}

emoji = tier_emoji.get(tournament_tier, "❓")
print(f"Tier {tournament_tier.upper()} {emoji}")
```

---

## 🌍 Nacionalidade do Campeonato - NÃO DISPONÍVEL ❌

### Campo: `tournament.country`

O PandaScore **NÃO traz** nacionalidade/país específico porque:

```json
{
  "tournament": {
    "type": "online",  // ← MOTIVO: campeonato é online
    "country": null,   // ← SEMPRE null para online
    "region": "EEU"    // ← SÓ temos região geográfica
  }
}
```

### Por Que `country` é Sempre `null`?

- **Eventos Online**: A maioria dos campeonatos CS2 são **100% online**, então não há um país físico associado
- **Eventos Offline/Híbridos**: Apenas eventos com `type: "offline"` ou `"online-and-offline"` teriam `country` preenchido

### Exemplo de Resposta Real

**Evento Online** (como os atuais):

```json
{
  "tournament": {
    "name": "European Contenders #2",
    "type": "online",
    "country": null,
    "region": "EEU"
  }
}
```

---

## 🗺️ O Que Temos de Alternativa: REGIÃO

### Campo: `tournament.region`

Como substituto para nacionalidade, a API fornece **região geográfica**:

```json
{
  "tournament": {
    "region": "EEU"  // ← Região disponível
  }
}
```

### Regiões Observadas

Conforme documentação da API PandaScore, os valores possíveis são:

| Código | Significado | Região |
|--------|-------------|--------|
| **ASIA** | Asia | Ásia |
| **EEU** | Eastern Europe Union | Leste Europeu |
| **ME** | Middle East | Oriente Médio |
| **NA** | North America | América do Norte |
| **OCE** | Oceania | Oceania |
| **SA** | South America | América do Sul |
| **WEU** | Western Europe Union | Oeste Europeu |

### Implementação da Região

```python
# Mapear região para país/emoji
region_info = {
    "ASIA": {"label": "� Ásia"},
    "EEU": {"label": "🇪🇺 Leste Europeu"},
    "ME": {"label": "🕌 Oriente Médio"},
    "NA": {"label": "�� América do Norte"},
    "OCE": {"label": "🇦🇺 Oceania"},
    "SA": {"label": "�� América do Sul"},
    "WEU": {"label": "�🇺 Oeste Europeu"},
}

region_code = match_data.get("tournament", {}).get("region", "unknown")
region_label = region_info.get(region_code, {}).get("label", "🌍 Regional")
```

---

## 📋 Dados Disponíveis no Tournament (Resumo Completo)

```json
{
  "tournament": {
    "id": 18006,
    "name": "Playoffs",
    "type": "online",
    "country": null,
    "region": "EEU",
    "tier": "d",
    "begin_at": "2025-11-10T15:30:00Z",
    "end_at": "2025-11-24T21:30:00Z",
    "winner_id": null,
    "has_bracket": true,
    "prizepool": "5,000 United States Dollar",
    "slug": "cs-go-cct-europe-...",
    "league_id": 5232,
    "modified_at": "2025-11-10T18:35:02Z"
  }
}
```

---

## 💡 Recomendações para Seu Bot

### Para Mostrar Nível do Campeonato

```python
# src/utils/embeds.py - Adicionar função auxiliar

def get_tournament_tier_emoji(tier: str) -> str:
    """Mapeia tier para emoji visualmente interessante."""
    tier_map = {
        "s": ("🏆 Tier S", "FFAA00"),  # Ouro
        "a": ("👑 Tier A", "FFFF00"),  # Amarelo
        "b": ("🥇 Tier B", "E0E0E0"),  # Prata
        "c": ("🥈 Tier C", "CD7F32"),  # Bronze
        "d": ("🥉 Tier D", "5E5E5E"),  # Cinza
    }
    return tier_map.get(tier, ("❓ Unknown", "CCCCCC"))

# Uso em match embed
tournament = match_data.get("tournament", {})
tier_label, tier_color = get_tournament_tier_emoji(tournament.get("tier", "unknown"))
```

### Para Mostrar Região (em vez de País)

```python
def get_region_display(region: str) -> str:
    """Converte código de região para display amigável."""
    region_map = {
        "EEU": "🇪🇺 Leste Europeu",
        "WEU": "🇪🇺 Oeste Europeu",
        "OCE": "🇦🇺 Oceania",
        "SA": "🇧🇷 América do Sul",
        "NA": "🇺🇸 América do Norte",
        "AS": "🌏 Ásia",
    }
    return region_map.get(region, "🌍 Regional")

# Uso em match embed
region = tournament.get("region", "unknown")
region_display = get_region_display(region)
```

---

## 🔍 Alternativas se Precisar de País Específico

Se você **REALMENTE** precisar de país específico além de região, opções:

1. **Parse do Nome**: Extrair do `league.name` ou `tournament.name`
   - Ex: "European Contenders #2" → inferir que é Europa
   - Não é 100% confiável

2. **Manter Banco de Dados Local**: Criar tabela mapping league_id → país

```sql
CREATE TABLE league_countries (
    league_id INT PRIMARY KEY,
    country_code VARCHAR(2),
    region VARCHAR(50),
    created_at TIMESTAMP
);
```

1. **Usar Apenas Região**: A maioria dos casos, a região é suficiente
   - Mais confiável que inferências

---

## 📝 Conclusão

| Pergunta | Resposta | Detalhes |
|----------|---------|----------|
| **Tier do Campeonato?** | ✅ **SIM** | Em `tournament.tier` (valores: d, c, b, a, s) |
| **Nacionalidade?** | ❌ **NÃO** | Campo `tournament.country` sempre null para eventos online |
| **Alternativa?** | ✅ **Região** | Em `tournament.region` (EEU, WEU, OCE, SA, NA, AS) |
| **Recomendação** | Usar Tier + Região | Combinar ambas para contexto completo do campeonato |

