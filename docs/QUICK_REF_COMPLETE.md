# Quick Reference: Tier, Regions e Streams

**Última Atualização**: 18 de Novembro de 2025

---

## 🏆 Tier Values

API Enum: `a | b | c | d | s | unranked` (+ null)

Ranking: **S > A > B > C > D > Unranked**

| Valor | Emoji | Label | Descrição |
|-------|-------|-------|-----------|
| s | 🏆 | Tier S - Elite | Major/Top |
| a | 👑 | Tier A - Top | Internacional |
| b | 🥇 | Tier B - Profissional | Regional Pro |
| c | 🥈 | Tier C - Semi-Pro | Semi-profissional |
| d | 🥉 | Tier D - Regional | Regional/Amador |
| unranked | ❓ | Unranked | Sem classificação |

---

## 🌍 Region Values

API Enum: `ASIA | EEU | ME | NA | OCE | SA | WEU` (+ null)

| Valor | Emoji | Label |
|-------|-------|-------|
| ASIA | 🌏 | Ásia |
| EEU | 🇪🇺 | Leste Europeu |
| ME | 🕌 | Oriente Médio |
| NA | 🇺🇸 | América do Norte |
| OCE | 🇦🇺 | Oceania |
| SA | 🇧🇷 | América do Sul |
| WEU | 🇪🇺 | Oeste Europeu |

---

## 💻 Event Type Values

API: `online | offline | online-and-offline`

| Valor | Emoji | Label |
|-------|-------|-------|
| online | 💻 | Online |
| offline | 🏟️ | Offline |
| online-and-offline | 🌐 | Online / Offline |

---

## 🎬 Streams List

Campo: `streams_list` (array de objects)

Cada stream tem:
- `embed_url` (uri | null) - URL para iframe
- `language` (string) - Código ISO 639-1 (pt, en, ru, etc)
- `main` (boolean) - É o stream principal?
- `official` (boolean) - É oficial?
- `raw_url` (uri) - URL no site da plataforma

Idiomas suportados: 125+ (ISO 639-1)

---

## 📝 Exemplo Completo

```json
{
  "tournament": {
    "tier": "d",
    "region": "SA",
    "type": "online"
  },
  "streams_list": [
    {
      "main": true,
      "language": "pt-BR",
      "official": true,
      "embed_url": "https://player.twitch.tv/?channel=cct_csgo",
      "raw_url": "https://twitch.tv/cct_csgo"
    }
  ]
}
```

Embed Output:
```
🎯 Detalhes do Campeonato
🥉 Tier D - Regional
🇧🇷 América do Sul
💻 Online
```

---

## 📁 Referência de Código

- **Mapa de Tier**: `src/utils/embeds.py` (TIER_MAP)
- **Mapa de Regions**: `src/utils/embeds.py` (REGION_MAP)
- **Mapa de Event Type**: `src/utils/embeds.py` (EVENT_TYPE_MAP)
- **Função Tier**: `get_tier_info(tier)`
- **Função Region**: `get_region_info(region)`
- **Função Event Type**: `get_event_type_info(event_type)`

---

## ✅ Checklist de Suporte

- ✅ Tiers: s, a, b, c, d, unranked
- ✅ Regions: ASIA, EEU, ME, NA, OCE, SA, WEU
- ✅ Event Types: online, offline, online-and-offline
- ✅ Languages: ISO 639-1 (125+)
- ✅ Fallbacks: unknown, null
- ✅ Testes: Passando

---

## 🧪 Teste

```bash
python scripts/test_tournament_info.py
```

Result: ✅ TESTE CONCLUÍDO COM SUCESSO
