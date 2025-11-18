# Quick Reference: Region Values

**API Enum**: ASIA | EEU | ME | NA | OCE | SA | WEU

---

## Mapeamento Rápido

| Code | Emoji | Label |
|------|-------|-------|
| ASIA | 🌏 | Ásia |
| EEU | 🇪🇺 | Leste Europeu |
| ME | 🕌 | Oriente Médio |
| NA | 🇺🇸 | América do Norte |
| OCE | 🇦🇺 | Oceania |
| SA | 🇧🇷 | América do Sul |
| WEU | 🇪🇺 | Oeste Europeu |

---

## Código em Uso

```python
REGION_MAP = {
    "ASIA": {"emoji": "🌏", "label": "Ásia"},
    "EEU": {"emoji": "🇪🇺", "label": "Leste Europeu"},
    "ME": {"emoji": "🕌", "label": "Oriente Médio"},
    "NA": {"emoji": "🇺🇸", "label": "América do Norte"},
    "OCE": {"emoji": "🇦🇺", "label": "Oceania"},
    "SA": {"emoji": "🇧🇷", "label": "América do Sul"},
    "WEU": {"emoji": "🇪🇺", "label": "Oeste Europeu"},
    "unknown": {"emoji": "🌍", "label": "Regional"},
}

def get_region_info(region):
    if not region:
        return REGION_MAP["unknown"]["emoji"], REGION_MAP["unknown"]["label"]
    region_data = REGION_MAP.get(region.upper(), REGION_MAP["unknown"])
    return (region_data["emoji"], region_data["label"])
```

---

## Localização em Produção

- **Mapa**: `src/utils/embeds.py` linha ~76
- **Função**: `get_region_info()` em `src/utils/embeds.py`
- **Teste**: `scripts/test_tournament_info.py`
- **Docs**: `docs/REGIAO_VALUES_API.md`
