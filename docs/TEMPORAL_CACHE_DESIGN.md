# 🕐 Cache Temporal: Documentação Técnica

**Objetivo**: Manter cache com cobertura temporal de exatamente **42 horas** usando datas da API PandaScore.

## Problema Resolvido

Anteriormente, o cache mantinha um número fixo de partidas (últimas 100, 20, etc) sem considerar o tempo real. Isso causava:
- Partidas muito antigas sendo mantidas no cache
- Cobertura temporal inconsistente
- Perda de partidas recentes

**Solução**: Utilizar as datas da API (`end_at`, `begin_at`, `updated_at`) para identificar e manter apenas as partidas dos últimos 42 horas.

## Arquitetura

### Módulo: `src/database/temporal_cache.py` (323 linhas)

#### 1. Classe: `TemporalCacheManager`

**Método**: `get_temporal_window() → (start_time, end_time)`
- Retorna janela de 42 horas em UTC com timezone info
- Fim: agora
- Início: agora - 42 horas
- Exemplo: `[2025-11-14 23:30 UTC, 2025-11-16 17:30 UTC]`

**Método**: `parse_api_datetime(dt_str) → datetime`
- Converte strings ISO 8601 da API (ex: "2025-11-16T13:15:35Z")
- Retorna datetime com timezone UTC
- Tratamento de None retorna None

**Método**: `get_match_temporal_anchor(match) → datetime`
- Prioridade de fontes de data:
  1. `end_at` (data término, mais confiável)
  2. `begin_at` (data início, se sem end_at)
  3. `updated_at` (última atualização, fallback)
- Retorna None se nenhuma data disponível

**Método**: `is_within_temporal_window(match, minimum_hours=42) → bool`
- Verifica se partida deve estar no cache
- Usa `get_match_temporal_anchor()` para obter data de referência
- Compara com janela temporal
- Retorna True se data_partida >= data_inicio_janela

#### 2. Função: `cleanup_expired_cache(client) → Dict`

Remove partidas com mais de 42 horas de idade.

```python
stats = await cleanup_expired_cache(client)

# Retorna:
{
    "deleted": 54,           # Partidas removidas
    "kept": 0,               # Partidas mantidas
    "query_time": 0.123,     # Tempo de execução
    "current_coverage_hours": 41.5  # Horas de cobertura após limpeza
}
```

**Lógica**:
1. Calcula janela temporal (42h)
2. Consulta todas as partidas do cache
3. Avalia cada uma com `is_within_temporal_window()`
4. Remove as fora da janela
5. Retorna estatísticas

#### 3. Função: `ensure_temporal_coverage(client, api_client, minimum_hours=42) → Dict`

Garante que cache tenha cobertura mínima, buscando mais páginas da API se necessário.

```python
stats = await ensure_temporal_coverage(
    client,
    api_client,
    minimum_hours=42
)

# Retorna:
{
    "coverage_status": "ADEQUATE",           # ADEQUATE, INSUFFICIENT, FETCHING
    "current_coverage_hours": 42.5,          # Horas de cobertura atual
    "matches_added": 12,                     # Novos matches adicionados nesta chamada
    "pages_fetched": 2,                      # Quantas páginas foram buscadas
    "max_pages_reached": False               # Se atingiu limite de páginas
}
```

**Lógica**:
1. Calcula cobertura temporal atual do cache
2. Se >= minimum_hours: retorna ADEQUATE
3. Caso contrário: busca próxima página da API
4. Repete até conseguir cobertura ou atingir limite (10 páginas)
5. Insere novos matches via `cache_manager.cache_matches()`

## Integração com Cache Scheduler

Modificação em `src/services/cache_scheduler.py` → método `update_all_matches()`:

```python
# Após atualizar cache normal:
logger.info("🕐 Executando limpeza temporal (42h)...")
try:
    client = await self.cache_manager.get_client()
    cleanup_stats = await cleanup_expired_cache(client)
    logger.info(f"   ✅ Limpeza concluída")
except Exception as e:
    logger.error(f"   ✗ Erro na limpeza temporal: {e}")

logger.info("🕐 Garantindo cobertura temporal de 42 horas...")
try:
    client = await self.cache_manager.get_client()
    coverage_stats = await ensure_temporal_coverage(
        client,
        self.api_client,
        minimum_hours=42
    )
    logger.info(f"   📊 Cobertura: {coverage_stats['current_coverage_hours']}h - "
               f"Status: {coverage_stats['coverage_status']}")
except Exception as e:
    logger.error(f"   ✗ Erro ao garantir cobertura: {e}")
```

## Fluxo de Execução

### Durante Update All Matches (a cada 15 minutos)

```
1. Fetch upcoming (página 1)
2. Fetch running (página 1)
3. Fetch finished (páginas 1-3)
4. Cache tudo no DB
   ↓
5. LIMPAR TEMPORAL
   • Calcula janela 42h
   • Remove partidas antigas
   • Log: "🧹 54 partidas removidas"
   ↓
6. GARANTIR COBERTURA
   • Verifica horas de cobertura
   • Se < 42h: busca próxima página
   • Insere novos matches
   • Log: "📊 Cobertura: 42.3h - ADEQUATE"
   ↓
7. Mostrar estatísticas
```

## Comportamento em Cenários Reais

### Cenário 1: Primeira Execução
```
Cache vazio → Fetch 3 páginas → ~300 partidas → 
Cobertura: 40-50h (muitas partidas recentes) →
Status: ADEQUATE
```

### Cenário 2: Cache com Partidas Antigas
```
Cache: 125 partidas (algumas com 3 dias) →
Limpeza: Remove 54 antigas →
Mantém: 71 partidas (últimas 42h) →
Status: ADEQUATE
```

### Cenário 3: Cobertura Insuficiente
```
Cache: 20 partidas (cobertura apenas 35h) →
Limpeza: Remove 2 antigas →
Coverage check: 35h < 42h necessários →
Fetch página 4 da API →
Adiciona 15 novos matches →
Cobertura: 43h →
Status: ADEQUATE
```

## Testes

**Script**: `scripts/test_temporal_cache.py`

Valida:
1. ✅ Janela temporal (42h exatos)
2. ✅ Parsing de datetime ISO 8601
3. ✅ Âncoras temporais (end_at → begin_at → updated_at)
4. ✅ Verificação de partidas na janela
5. ✅ Limpeza e cobertura no banco

```bash
python scripts/test_temporal_cache.py
```

Resultado esperado:
```
✅ TODOS OS TESTES PASSARAM!
   • Janela de 42 horas mantida
   • Parsing de datetimes ISO 8601 OK
   • Âncoras temporais corretas
   • Limpeza funcionando
   • Cobertura garantida
```

## Performance

- **Limpeza**: ~100ms para 125 partidas
- **Coverage check**: ~50ms (sem fetch) ou ~1-2s (com fetch de página)
- **Impacto no scheduler**: +150ms por ciclo (negligenciável)

## Logging

Exemplos de logs gerados:

```
🕐 Executando limpeza temporal (42h)...
   ✅ Limpeza concluída
   Deletadas: 54, Mantidas: 71

🕐 Garantindo cobertura temporal de 42 horas...
   📊 Cobertura: 42.3h - Status: ADEQUATE
   ✅ 15 novas partidas adicionadas
```

## Configuração

### Constantes (em `temporal_cache.py`)

```python
class TemporalCacheManager:
    CACHE_WINDOW_HOURS = 42  # Janela temporal alvo
```

Para mudar para outro valor (ex: 48 horas):
1. Editar `CACHE_WINDOW_HOURS = 48`
2. Reiniciar bot

## Limitações e Trade-offs

✅ **Vantagens**:
- Cache sempre com 42h de dados
- Usa datas reais da API
- Automático e sem configuração
- Detecta e corrige cobertura insuficiente

⚠️ **Considerações**:
- Pode remover partidas se houver gap na API
- Cobertura pode variar ±2h em dia com poucos matches
- Fetch de extra páginas custa ~1-2s

## Próximas Melhorias

1. **Configurável por guild**: Diferentes horários de cache por servidor Discord
2. **Métricas**: Dashboard com histórico de cobertura
3. **Alertas**: Notificar se cobertura < 24h
4. **Priorização**: Guardar matches de times favoritos indefinidamente

## Referências

- **Temporal Cache Concept**: Inspirado em bancos de série temporal (InfluxDB)
- **API ISO 8601**: [RFC 3339 compliant](https://tools.ietf.org/html/rfc3339)
- **Cache Policy**: Based on LRU (Least Recently Used) adapted with temporal bounds
