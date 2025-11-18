# 🕐 Scripts de Teste de Timezone

Conjunto completo de scripts para validar e testar a implementação de timezone do bot.

## 📋 Scripts Disponíveis

### 1. `test_timezone_with_real_data.py` - Teste com Dados Reais
**Objetivo**: Validar conversões com dados reais da API PandaScore e do banco de dados.

**Execução**:
```bash
python scripts/test_timezone_with_real_data.py
```

**O que testa**:
- ✅ Dados reais da API PandaScore (partidas futuras, ao vivo, passadas)
- ✅ Dados reais do cache do banco de dados
- ✅ Conversão para múltiplos timezones (Brasil, UK, Japão, EUA)
- ✅ Discord timestamps dinâmicos
- ✅ Validação de timezones

**Saída**:
```
🌐 TESTE 1: Dados Reais da API PandaScore
📅 Buscando partidas FUTURAS da API...
✓ Encontradas 3 partidas futuras

📊 Testando 3 partidas FUTURAS em 4 timezones:
🎮 Partida #1
  ID: 12345 | Status: not_started
  UTC Original: 2025-11-20 15:00:00+00:00
  🇧🇷 America/Sao_Paulo     → 20/11 12:00 (BRT UTC-3)
  🇬🇧 Europe/London         → 20/11 15:00 (GMT UTC+0)
  🇯🇵 Asia/Tokyo            → 21/11 00:00 (JST UTC+9)
  🇺🇸 America/New_York      → 20/11 10:00 (EST UTC-5)
```

**Requisitos**:
- Bot deve ter rodado pelo menos uma vez (`python -m src.bot`)
- Cache deve ter dados (`python -m src.database.build_db`)
- API key configurada em `.env`

---

### 2. `validate_timezone_correctness.py` - Validador de Correctness
**Objetivo**: Validar se as conversões estão matematicamente corretas.

**Execução**:
```bash
python scripts/validate_timezone_correctness.py
```

**O que testa**:
- ✅ Conversões matemáticas precisas
- ✅ Validação de hora esperada vs obtida
- ✅ Validação de dia esperado vs obtido
- ✅ 10 casos de teste padrão

**Casos de Teste Padrão**:
```
Partida 15:00 UTC em Brasil          → 12:00 (15 - 3)
Partida 15:00 UTC em Londres         → 15:00 (15 + 0)
Partida 15:00 UTC em Tóquio          → 00:00 próximo dia (15 + 9)
Madrugada 03:00 UTC em Brasil        → 00:00 (3 - 3)
Madrugada 03:00 UTC em Tóquio        → 12:00 (3 + 9)
Fim do dia 23:00 UTC em Brasil       → 20:00 (23 - 3)
Fim do dia 23:00 UTC em Tóquio       → 08:00 próximo dia (23 + 9)
Meio-dia 12:00 UTC em New York       → 07:00 (12 - 5)
Meio-dia 12:00 UTC em Sydney         → 23:00 (12 + 11)
Meia-noite 00:00 UTC em Brasil       → 21:00 dia anterior (0 - 3)
```

**Saída**:
```
🔍 VALIDADOR DE CORRECTNESS DE TIMEZONE
✅ PASSOU
  📝 Partida 15:00 UTC em Brasil
  🌍 UTC: 20/11 15:00 → America/Sao_Paulo (🇧🇷 BRT UTC-3)
  🕐 Esperado: 20/12:00 | Obtido: 20/12:00

✅ PASSOU
  📝 Partida 15:00 UTC em Tóquio (próximo dia)
  🌍 UTC: 20/11 15:00 → Asia/Tokyo (🇯🇵 JST UTC+9)
  🕐 Esperado: 21/00:00 | Obtido: 21/00:00

📊 RESUMO
✅ Testes bem-sucedidos: 10/10 (100%)
❌ Testes falhados: 0/10
🎉 TODOS OS TESTES PASSARAM! A lógica de timezone está correta.
```

**Requisitos**:
- Nenhum, usa apenas a lógica de TimezoneManager

---

### 3. `interactive_timezone_converter.py` - Conversor Interativo
**Objetivo**: Testar conversões manualmente de forma interativa.

**Execução**:
```bash
python scripts/interactive_timezone_converter.py
```

**Menu**:
```
⏰ CONVERSOR INTERATIVO DE TIMEZONE

📋 Opções:
  1. Converter hora UTC para um timezone
  2. Converter hora para múltiplos timezones
  3. Listar timezones comuns
  4. Validar timezone
  5. Ver offsets de todos timezones comuns
  6. Sair
```

**Exemplos de Uso**:

**Exemplo 1**: Converter 15:00 UTC para Brasil
```
Escolha uma opção: 1
Digite a hora: 15:00
Timezone: America/Sao_Paulo

✅ Resultado:
  UTC:      15:00
  America/Sao_Paulo 🇧🇷
  Local:    12:00
  Offset:   UTC-3
  Sigla:    BRT
  Discord:  <t:1732077000:t>
```

**Exemplo 2**: Listar timezones comuns
```
Escolha uma opção: 3

📋 TIMEZONES COMUNS
  Código | Timezone
  ------+------------------------------------------
    1   | 🇧🇷 America/Sao_Paulo     (BRT UTC-3)
    2   | 🇺🇸 America/New_York       (EST UTC-5)
    3   | 🇬🇧 Europe/London          (GMT UTC+0)
    4   | 🇫🇷 Europe/Paris           (CET UTC+1)
    5   | 🇯🇵 Asia/Tokyo             (JST UTC+9)
    6   | 🇦🇺 Australia/Sydney       (AEDT UTC+11)
    7   | 🇦🇪 Asia/Dubai             (GST UTC+4)
    8   | 🇨🇳 Asia/Shanghai          (CST UTC+8)
```

**Requisitos**:
- Nenhum, modo interativo puro

---

### 4. `benchmark_timezone_performance.py` - Benchmark de Performance
**Objetivo**: Validar que conversões não impactam latência do bot.

**Execução**:
```bash
python scripts/benchmark_timezone_performance.py
```

**O que testa**:
- ✅ Parse de ISO datetime (10.000 iterações)
- ✅ Conversão UTC → Timezone (10.000 iterações)
- ✅ Formatação para exibição (10.000 iterações)
- ✅ Discord timestamp (10.000 iterações)
- ✅ Validação de timezone (10.000 iterações)
- ✅ Múltiplos timezones (5.000 iterações com 5 timezones)
- ✅ Pipeline completo (1.000 iterações)

**Saída**:
```
⚡ BENCHMARK DE PERFORMANCE DE TIMEZONE

⏱️  TESTES INDIVIDUAIS (10.000 iterações cada)

1️⃣  Parse ISO DateTime:
   Total:   12.34 ms
   Média:   0.0012 ms por operação
   Throughput: 810457 ops/seg

2️⃣  Conversão UTC → Timezone Local:
   Total:   23.45 ms
   Média:   0.0023 ms por operação
   Throughput: 426573 ops/seg

3️⃣  Formatação para Exibição:
   Total:   18.67 ms
   Média:   0.0019 ms por operação
   Throughput: 535885 ops/seg

📊 RESUMO DE PERFORMANCE
Operação                     Tempo Médio    Throughput
----------------------------------------------------------
Parse ISO DateTime           0.0012 ms      810457 ops/s
Conversão UTC → Timezone     0.0023 ms      426573 ops/s
Formatação para Exibição     0.0019 ms      535885 ops/s
Discord Timestamp            0.0025 ms      394570 ops/s
Validação de Timezone        0.0015 ms      661376 ops/s
Conversão (5 timezones)      0.0023 ms      423858 ops/s
Pipeline Completo            0.0089 ms      112359 ops/s

✔️  Validação de Latência:
  ✅ Pipeline 0.0089 ms - EXCELENTE (< 1ms)
```

**Requisitos**:
- Nenhum, usa apenas TimezoneManager

---

## 🚀 Como Executar os Testes Completos

### Sequência Recomendada:

```bash
# 1. Validar correctness (rápido, sem dependências)
python scripts/validate_timezone_correctness.py

# 2. Benchmark (validar latência)
python scripts/benchmark_timezone_performance.py

# 3. Teste interativo (explorar conversões)
python scripts/interactive_timezone_converter.py

# 4. Teste com dados reais (requer bot em execução)
python -m src.bot &  # Em outra aba
sleep 30  # Deixar cache popular
python scripts/test_timezone_with_real_data.py
```

### Script de Teste Automatizado:

```bash
#!/bin/bash
# scripts/run_all_timezone_tests.sh

echo "🕐 Executando todos os testes de timezone..."

echo -e "\n1. Validando correctness..."
python scripts/validate_timezone_correctness.py

echo -e "\n2. Executando benchmark..."
python scripts/benchmark_timezone_performance.py

echo -e "\n3. Testando com dados reais..."
python scripts/test_timezone_with_real_data.py

echo -e "\n✅ Todos os testes concluídos!"
```

---

## ✅ Checklist de Validação

Quando implementar timezone nos embeds, use estes scripts para validar:

- [ ] `validate_timezone_correctness.py` → 100% de sucesso
- [ ] `benchmark_timezone_performance.py` → Pipeline < 1ms
- [ ] `test_timezone_with_real_data.py` → Conversões corretas
- [ ] `interactive_timezone_converter.py` → Explorar casos edge

---

## 📊 Interpretando Resultados

### Correctness (validate_timezone_correctness.py)
- ✅ **100% de sucesso**: Lógica matemática está correta
- ⚠️ **80-99% de sucesso**: Investigar testes falhados
- ❌ **< 80% de sucesso**: Há bug na lógica de conversão

### Performance (benchmark_timezone_performance.py)
- ✅ **< 1ms**: Excelente, não impacta latência
- ✅ **1-5ms**: Bom, aceitável para bot Discord
- ⚠️ **5-10ms**: Aceitável mas monitorar
- ❌ **> 10ms**: Pode impactar experiência do usuário

### Real Data (test_timezone_with_real_data.py)
- ✅ **Todos os timezones convertidos**: Implementação completa
- ⚠️ **Alguns timezones falhados**: Investigar específicos
- ⚠️ **Sem dados de API**: Usar cache ou dados de teste

---

## 🐛 Resolvendo Problemas

### "Import pytz could not be resolved"
```bash
# Ativar venv
source venv/bin/activate

# Instalar pytz
pip install pytz

# Verificar
python -c "import pytz; print('✓ pytz importado')"
```

### "Nenhuma partida encontrada no cache"
```bash
# Atualizar cache primeiro
python -m src.database.build_db

# Ou rodar o bot para popular
python -m src.bot

# Depois executar testes
python scripts/test_timezone_with_real_data.py
```

### "Timezone inválido"
Use o script interativo para listar timezones válidos:
```bash
python scripts/interactive_timezone_converter.py
# Opção 3: Listar timezones comuns
# Opção 4: Validar um timezone
```

---

## 📈 Métricas Esperadas

| Operação | Tempo Esperado | Status |
|----------|----------------|--------|
| Parse ISO | < 0.002 ms | ✅ |
| Conversão | < 0.003 ms | ✅ |
| Formatação | < 0.002 ms | ✅ |
| Discord Timestamp | < 0.003 ms | ✅ |
| Pipeline Completo | < 0.010 ms | ✅ |

---

## 🎯 Próximas Etapas

Após validar estes scripts:

1. ✅ Atualizar `src/utils/embeds.py` com suporte a timezone
2. ✅ Atualizar `src/cogs/matches.py` para passar timezone
3. ✅ Testar em Discord com diferentes servidores
4. ✅ Monitorar em produção

---

**Criado em**: 18 de Novembro de 2025  
**Última atualização**: [data]  
**Status**: ✅ Pronto para uso
