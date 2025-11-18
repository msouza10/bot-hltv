# Implementação: Tier, Region e Event Type nos Embeds

**Data**: 18 de Novembro de 2025  
**Status**: ✅ Implementado e Testado

## Resumo Executivo

Adicionado informações de Tier do Campeonato, Região Geográfica e Tipo de Evento aos embeds do Discord.

Os dados já eram capturados pela API e cacheados, mas não eram exibidos nos embeds. Agora são mostrados em um novo campo chamado **"🎯 Detalhes do Campeonato"**.

## O Que Foi Implementado

### 1. Novo Campo nos Embeds

Adicionado campo **"🎯 Detalhes do Campeonato"** com:
- Tier (d, c, b, a, s)
- Região (EEU, WEU, NA, SA, OCE, AS)
- Tipo de Evento (online, offline, online-and-offline)

Exemplo de saída:
```
🎯 Detalhes do Campeonato
🥉 Tier D - Regional
🇪🇺 Leste Europeu
💻 Online
```

### 2. Funções Auxiliares em `src/utils/embeds.py`

**get_tier_info(tier)** - Formata tier com emoji e label
**get_region_info(region)** - Formata região com emoji e label  
**get_event_type_info(event_type)** - Formata tipo de evento com emoji e label

### 3. Mapas de Dados

TIER_MAP - Mapeia tiers para emoji e descrição
REGION_MAP - Mapeia regiões para emoji e descrição
EVENT_TYPE_MAP - Mapeia tipos de evento para emoji

## Onde Foi Adicionado

- `create_match_embed()` - Embeds de partidas futuras
- `create_result_embed()` - Embeds de resultados finalizados

## Cache

Os dados **já estavam sendo cacheados** automaticamente:
- Campo `match_data` preserva todo o JSON do match
- Inclui `tournament.tier`, `tournament.region`, `tournament.type`
- Nenhuma alteração necessária no cache_manager.py

## Teste

Script criado: `scripts/test_tournament_info.py`

Execução:
```bash
cd /home/msouza/Documents/bot-hltv
python scripts/test_tournament_info.py
```

Resultado: ✅ TESTE CONCLUÍDO COM SUCESSO

## Como Usar

1. Iniciar bot: `python -m src.bot`
2. Usar comandos Discord: `/partidas`, `/aovivo`, `/resultados`
3. Procurar pelo campo "🎯 Detalhes do Campeonato"

## Arquivos Modificados

- `src/utils/embeds.py` - Adicionadas funções e campos
- `scripts/test_tournament_info.py` - Novo script de teste

## Comportamento com Dados Faltantes

Cada função trata gracefully valores None ou desconhecidos:

```
get_tier_info(None) → ("❓", "Tier Desconhecido")
get_region_info("FOO") → ("🌍", "Regional")
get_event_type_info(None) → ("❓", "Tipo Desconhecido")
```

## Exemplos de Saída

### Tier D, Leste Europeu, Online
```
🥉 Tier D - Regional
🇪🇺 Leste Europeu
💻 Online
```

### Tier S, Oeste Europeu, Online
```
🏆 Tier S - Elite
🇪🇺 Oeste Europeu
💻 Online
```

### Tier A, América do Norte, Offline
```
👑 Tier A - Top
🇺🇸 América do Norte
🏟️ Offline
```

## Referência de Valores

**Tiers**: d (Regional), c (Semi-Pro), b (Profissional), a (Top), s (Elite)

**Regiões**: EEU (Leste Europeu), WEU (Oeste Europeu), NA (América do Norte), SA (América do Sul), OCE (Oceania), AS (Ásia)

**Tipos**: online, offline, online-and-offline

## Documentação Relacionada

Veja também:
- docs/ANALISE_TIER_NACIONALIDADE.md
- docs/ANALISE_ESTRUTURA_API_PANDASCORE.md
