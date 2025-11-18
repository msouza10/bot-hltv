# Valores de Region da API PandaScore

**Data**: 18 de Novembro de 2025  
**Fonte**: Documentação da API PandaScore  
**Status**: ✅ Atualizado

---

## Enum de Regions

Conforme documentação da API, o campo `tournament.region` retorna um dos 8 valores fixos:

```
ASIA  EEU  ME  NA  OCE  SA  WEU
```

---

## Mapeamento Completo

| Código | Full Name | Emoji | Label em PT |
|--------|-----------|-------|-------------|
| **ASIA** | Asia | 🌏 | Ásia |
| **EEU** | Eastern Europe Union | 🇪🇺 | Leste Europeu |
| **ME** | Middle East | 🕌 | Oriente Médio |
| **NA** | North America | 🇺🇸 | América do Norte |
| **OCE** | Oceania | 🇦🇺 | Oceania |
| **SA** | South America | 🇧🇷 | América do Sul |
| **WEU** | Western Europe Union | 🇪🇺 | Oeste Europeu |

---

## Implementação em Código

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
```

---

## Exemplos de Uso

### Oriente Médio
```
🎯 Detalhes do Campeonato
🥉 Tier D - Regional
🕌 Oriente Médio
💻 Online
```

### Ásia
```
🎯 Detalhes do Campeonato
🥇 Tier B - Profissional
🌏 Ásia
💻 Online
```

### Leste Europeu
```
🎯 Detalhes do Campeonato
🥉 Tier D - Regional
🇪🇺 Leste Europeu
💻 Online
```

---

## Tratamento de Fallbacks

- Se `region` for `null`: Usar emoji 🌍 com label "Regional"
- Se `region` for desconhecido: Usar emoji 🌍 com label "Regional"
- Se `region` for "AS" (abreviado): Tratar como "ASIA"

---

## Arquivo de Referência

Implementação em: `src/utils/embeds.py`
- Mapa: `REGION_MAP`
- Função: `get_region_info(region: str)`

Teste em: `scripts/test_tournament_info.py`
- Testa todos os 8 valores + null + unknown
