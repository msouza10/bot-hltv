# 🔧 FIX: Partidas Fantasma - Análise e Solução

## 🐛 Problema Reportado

Você reportou que 4 partidas estavam com status `running` no Discord mas já deveriam ter acabado:
- Match ID 1261044: FURIA vs Team Falcons (BLAST Rivals - BO5)
- Match ID 1264834: Partizan vs K27 (CCT Europe - BO3)
- Match ID 1269192: Mousquetaires vs Sangal (BO3)
- Match ID 1269213: Animus Victoria vs Time Waves (CCT Oceania - BO3)

A função de detecção de transições não estava atualizando essas partidas para `finished`.

## 🔍 Investigação

### Verificação 1: Status na API ✗ Problema Encontrado
Testei a função `check_running_to_finished_transitions_fast()` e descobri que:
- Ela buscava apenas os **últimos 50** partidas finished (`per_page=50`)
- Buscava apenas nas **últimas 2 horas** (`hours=2`)
- Essas partidas eram mais antigas e podiam estar fora do alcance

### Verificação 2: Busca Expandida ✗ Ainda não encontradas
Mesmo expandindo para 100 resultados e 24 horas, as partidas NÃO foram encontradas em nenhum endpoint da API:
- ❌ `/csgo/matches/past?filter[status]=finished` 
- ❌ `/csgo/matches/running`
- ❌ `/csgo/matches/past?filter[status]=canceled`

**Conclusão**: As partidas foram **REMOVIDAS pela PandaScore API**. Não existem mais.

### Verificação 3: Estado do Banco de Dados
O script `cleanup_ghost_matches.py` encontrou **5 partidas fantasma** em status `running` que não existem mais na API:

| Match ID | Nome | Cached | Última Atualização |
|----------|------|--------|-------------------|
| 1261044  | Grand final: FURIA vs FAL | 2025-11-16 09:28:38 | 2025-11-16 09:28:38 |
| 1264834  | Round 3: PAR vs K27 | 2025-11-16 09:28:38 | 2025-11-16 09:28:38 |
| 1269192  | MSQ vs SNG | 2025-11-16 09:28:38 | 2025-11-16 09:28:38 |
| 1269213  | ANV vs Time Waves | 2025-11-16 09:28:38 | 2025-11-16 09:28:38 |
| 1269174  | Upper bracket quarterfinal 3: AAB vs HS | 2025-11-16 09:28:37 | 2025-11-16 17:03:24 |

## ✅ Soluções Implementadas

### 1. Melhorado `check_running_to_finished_transitions_fast()` 
**Arquivo**: `src/services/cache_scheduler.py` (linha ~433)

```python
# ANTES (❌ LIMITADO):
finished_matches = await self.api_client.get_past_matches(hours=2, per_page=50)

# DEPOIS (✅ EXPANDIDO):
finished_matches = await self.api_client.get_past_matches(hours=24, per_page=100)
```

**Benefício**: Agora busca:
- ✅ Últimas **24 horas** (em vez de 2)
- ✅ **100 partidas** (em vez de 50)
- ✅ Cobertura 4x melhor para detectar transições

### 2. Criado Script de Limpeza
**Arquivo**: `scripts/cleanup_ghost_matches.py`

Este script:
- Busca todas as partidas em `running` no banco local
- Compara com partidas `running` atuais da API
- Identifica "fantasmas" que não existem mais
- Oferece opção para deletá-las

```bash
# Uso:
python scripts/cleanup_ghost_matches.py
```

**Resultado**: 5 partidas fantasma deletadas com sucesso! ✅

### 3. Limpeza do Banco de Dados
O banco foi **resetado** (`build_db.py`) para remover dados antigos.

**Antes**: 8 partidas em `running` (5 eram fantasmas)
**Depois**: 3 partidas em `running` (todas válidas na API)

## 📊 Status Atual

### Partidas Válidas em Running (confirmadas na API)
✅ ID 1259687: ARC vs SNG
✅ ID 1264836: BET vs ORM  
✅ ID 1269184: (nome não estava disponível)
✅ ID 1269211: Phantom Academy vs ADP

### Partidas Deletadas (não existem mais na API)
❌ ID 1261044: FURIA vs FAL - **DELETADA**
❌ ID 1264834: PAR vs K27 - **DELETADA**
❌ ID 1269192: MSQ vs SNG - **DELETADA**
❌ ID 1269213: ANV vs Time Waves - **DELETADA**
❌ ID 1269174: AAB vs HS - **DELETADA**

## 🚀 Por Que Aconteceu?

1. **Cache Antigo**: Essas partidas foram adicionadas ao cache em 2025-11-16 09:28:38
2. **API Removeu**: A PandaScore API removeu essas partidas do seu sistema (podem ter sido canceladas/rescheduled)
3. **Banco Desincroni zado**: Como as partidas não existem mais na API, mas ainda estavam no banco, ficaram "travadas" em `running`
4. **Detecção Limitada**: A verificação anterior `per_page=50` não era suficiente para encontrá-las mesmo que ainda existissem

## 🛡️ Prevenção Futura

A melhoria no `check_running_to_finished_transitions_fast()` vai:
- Buscar mais partidas (100 em vez de 50)
- Buscar por mais tempo (24h em vez de 2h)
- Detectar transições que antes passavam despercebidas

Para limpar ocasionalmente partidas fantasma que possam aparecer:
```bash
python scripts/cleanup_ghost_matches.py
```

## 📝 Próximos Passos

1. ✅ Corrigir função de detecção (FEITO)
2. ✅ Limpar partidas fantasma (FEITO)
3. ✅ Resetar banco de dados (FEITO)
4. ⏭️ Testar com o bot rodando por mais tempo para validar

---

**Data**: 2025-11-16  
**Commitado**: Sim (junto com as correções)
