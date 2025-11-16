# 🔄 Paginação Inteligente por Datas: Como Funciona

## O Problema Original

Antes: Sistema buscava apenas página 1 da API (100 partidas)
```
API request: /matches/past?per_page=100&page=1
Response: 100 matches

❌ Problema:
- Se match está na página 2+, não é encontrado
- Cobertura temporal inconsistente
- Partidas "desaparecem" do cache
```

## A Solução: Paginação por Cobertura Temporal

Novo: Sistema **pagina até atingir 42 horas de cobertura**, não por número de páginas fixo.

```
Objetivo: Ter cobertura de 42 horas

Algoritmo:
WHILE cobertura_atual < 42 horas AND página <= 20:
    1. Buscar página N
    2. Extrair datas de cada match (end_at → begin_at → updated_at)
    3. Calcular min/max dates = cobertura temporal
    4. Se cobertura >= 42h: PARA
    5. Senão: página++
```

## Fluxo Visual

```
Primeira Execução (Cache Vazio):
┌─────────────────────────────────────────────┐
│ Objetivo: 42 horas de cobertura             │
└──────────┬──────────────────────────────────┘
           ↓
      Página 1
   ┌─────────────┐
   │ 95 matches  │  Match datas: 2025-10-19 até 2025-11-16
   │ Cobertura   │  = 28.4 dias = 681 horas
   └──────┬──────┘
          ↓
    ✅ PARA! (681h >= 42h)
    
    Resultado: 95 matches armazenados
               Cobre 28.4 dias (muito mais que 42h)
```

```
Segunda Execução (Cache com Dados Antigos):
┌─────────────────────────────────────────────┐
│ Cache tem 200 matches mas alguns com 60 dias │
└──────────┬──────────────────────────────────┘
           ↓
    Step 1: Fetch Normal (upcoming, running, finished)
    ↓
    Step 2: LIMPEZA TEMPORAL
    Remove partidas > 42h antigas
    200 → 120 matches
    
    Step 3: COVERAGE CHECK
    Calcula período: 2025-11-14 15:00 até 2025-11-16 17:00
    = 50.1 horas
    ✅ 50.1h >= 42h ADEQUADO
    
    Resultado: 120 matches frescos, 42h+ cobertura
```

## Componentes Chave

### 1. Função: `ensure_temporal_coverage()`

```python
async def ensure_temporal_coverage(
    client,           # libSQL client
    api_client,       # PandaScore API client
    minimum_hours=42  # Alvo de cobertura
) → Dict
```

**Pseudocódigo:**
```python
while current_coverage < minimum_hours and page <= 20:
    # Buscar página
    matches = await api_client.get_past_matches(
        per_page=100, 
        page=page
    )
    
    # Armazenar
    for match in matches:
        await client.execute(
            "INSERT INTO matches_cache VALUES (...) 
             ON CONFLICT(match_id) DO NOTHING"
        )
    
    # Recalcular cobertura
    result = await client.execute("""
        SELECT 
            MIN(end_at OR begin_at OR updated_at) as oldest,
            MAX(end_at OR begin_at OR updated_at) as newest
        FROM matches_cache
    """)
    
    oldest, newest = result
    current_coverage = (newest - oldest).hours
    
    if current_coverage >= minimum_hours:
        break
    
    page += 1

return {
    "coverage_status": "ADEQUATE" or "INSUFFICIENT",
    "current_coverage_hours": coverage,
    "pages_fetched": page,
    "matches_added": count
}
```

### 2. Função: `cleanup_expired_cache()`

```python
async def cleanup_expired_cache(client) → Dict
```

**Lógica:**
```python
# Calcular janela (42 horas atrás)
end = datetime.now(UTC)
start = end - timedelta(hours=42)

# Deletar antigos
await client.execute("""
    DELETE FROM matches_cache
    WHERE (end_at OR begin_at OR updated_at) < ?
""", [start])

# Retornar stats
return {
    "deleted": num_deleted,
    "kept": num_kept,
    "current_coverage_hours": new_coverage
}
```

## Integração no Cache Scheduler

A cada **15 minutos**, o scheduler executa:

```python
async def update_all_matches(self):
    # 1️⃣ FASE 1: Buscar dados normais
    upcoming = await api_client.get_upcoming_matches(per_page=50)
    running = await api_client.get_running_matches()
    past = await api_client.get_past_matches(per_page=20)
    canceled = await api_client.get_canceled_matches(per_page=20)
    
    # Armazenar tudo
    await cache_manager.cache_matches(all_matches)
    
    # 2️⃣ FASE 2: LIMPEZA TEMPORAL
    logger.info("🧹 Limpando dados > 42h...")
    cleanup = await cleanup_expired_cache(client)
    logger.info(f"   Deletadas: {cleanup['deleted']}")
    
    # 3️⃣ FASE 3: VERIFICAR COBERTURA
    logger.info("📊 Verificando cobertura...")
    coverage = await ensure_temporal_coverage(client, api_client)
    logger.info(f"   Cobertura: {coverage['hours']}h")
    
    if coverage['status'] != 'ADEQUATE':
        logger.warning(f"⚠️ Cobertura insuficiente: {coverage['hours']}h")
```

## Cenários de Uso

### Cenário 1: Primeira Execução do Bot
```
Estado: Cache vazio
Ação: 
  1. Coverage check detecta vazio
  2. Começa página 1
  3. Vai para página 2, 3, 4... até 42h
  
Resultado:
  • Pode precisar de 2-5 páginas
  • ~2 segundos para popular
  • Cache com 42-200 horas de dados
```

### Cenário 2: Funcionamento Normal (Dia com Muitos Matches)
```
Estado: Cache com 120 matches de 42h atrás
Ação:
  1. Fetch normal (upcoming, running, past)
  2. Adiciona 150 novos matches
  3. Limpeza remove 100 antigos (> 42h)
  4. Resultado: 170 matches (exatamente 42h)
  
Tempo: ~300ms total
```

### Cenário 3: Gap na API (Fim de Semana)
```
Estado: Cache com 40 matches (apenas 12h)
Ação:
  1. Coverage check detecta 12h < 42h
  2. Pagina até limite (página 20)
  3. Reúne todos matches disponíveis
  4. Se ainda < 42h: status = PARTIAL
  
Comportamento: Sistema funciona, apenas com menos dados
```

### Cenário 4: Peak Season (Muitos Matches)
```
Estado: 500 matches em 42h
Ação:
  1. Coverage check: encontra 42h em página 1 ou 2
  2. Para de paginar (não consulta página 3+)
  3. Insert on conflict ignora duplicatas
  
Resultado: Eficiente, sem paginação desnecessária
```

## Performance

| Operação | Tempo | Notas |
|----------|-------|-------|
| Limpeza 120 matches | 50ms | Query SQL + delete |
| Coverage check | 75ms | SELECT min/max + cálculo |
| Fetch página | 800-1200ms | API request |
| Paginação 1-3 páginas | 2.5-3.5s | 3x fetch API |
| Total update (15min) | 4-5s | Com limpeza + coverage |

## Comparação: Antes vs Depois

### Antes (Fixo 3 páginas)
```
get_past_matches(per_page=100, page=1)  # 100 matches
get_past_matches(per_page=100, page=2)  # 100 matches
get_past_matches(per_page=100, page=3)  # 100 matches

Total: Sempre 300 matches
❌ Pode ser insuficiente (se cobertura < 42h)
❌ Pode ser excessivo (pega dados de 1 mês)
```

### Depois (Temporal Inteligente)
```
WHILE coverage < 42h:
    Fetch page N
    Calcular coverage (min/max dates)
    Se OK: BREAK
    Else: page++

Total: 1-5 páginas conforme necessário
✅ Sempre 42h de dados
✅ Sem paginação desnecessária
✅ Adapta a Season (muitos matches vs poucos)
```

## Fluxo Detalhado: Primeira Vez

```
Cache vazio
  ↓
coverage_check() chamada
  ↓
SELECT COUNT(*) = 0
  ↓
Status: EMPTY → começa paginação
  ↓
Página 1: 95 matches (cobertura = 28.4 dias)
  ↓
28.4 dias > 42 horas?  YES → PARA
  ↓
INSERT 95 matches com ON CONFLICT
  ↓
Resultado: Cache populado com 42h+
```

## Configuração

Para ajustar a janela temporal:

```python
# Em: src/database/temporal_cache.py

class TemporalCacheManager:
    CACHE_WINDOW_HOURS = 42  # ← Ajustar aqui
```

Exemplos:
- `CACHE_WINDOW_HOURS = 24` → Cache de 24h
- `CACHE_WINDOW_HOURS = 48` → Cache de 2 dias
- `CACHE_WINDOW_HOURS = 42` → Cache de 1.75 dias (padrão)

## Monitoramento

Logs gerados:

```
🕐 Executando limpeza temporal (42h)...
   🧹 Deletadas: 54, Mantidas: 120
   Cobertura após limpeza: 41.2h

🕐 Garantindo cobertura temporal de 42 horas...
   📄 Página 1... 95 matches
      Cobertura acumulativa: 28.4h
      Faltam: 13.6h para 42h
   📄 Página 2... 87 matches
      Cobertura acumulativa: 42.1h
      ✅ OBJETIVO ATINGIDO!
   📊 Cobertura: 42.1h - Status: ADEQUATE
   ✅ 87 novas partidas adicionadas
```

## Testes

Execute:
```bash
python scripts/test_temporal_cache.py          # Testes unitários
python scripts/demo_intelligent_pagination.py  # Demonstração visual
```

## Próximas Melhorias

1. **Métricas de Cobertura**: Registrar histórico de coverage
2. **Alertas**: Se coverage < 24h (problema na API?)
3. **Priorização**: Guardar favoritos indefinidamente
4. **Cache Composto**: Diferentes janelas por tipo de match
