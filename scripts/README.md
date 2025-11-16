# 🛠️ Guia de Scripts Disponíveis

Scripts de teste, debug e utilidade estão organizados em `scripts/`

## 📋 Scripts Disponíveis

### 1️⃣ **init_db.py** - Inicializar Banco de Dados
```bash
python scripts/init_db.py
```
- **Quando usar**: Primeira vez configurando o projeto
- **O que faz**: Cria tabelas SQLite, inicializa schema
- **Resultado**: `data/bot.db` criado e pronto

---

### 2️⃣ **validate_cache_full.py** - Validar Cache Completo
```bash
python scripts/validate_cache_full.py
```
- **Quando usar**: Verificar se cache está ok, todos os dados presentes
- **O que faz**: 
  - Lista todas as partidas em cache
  - Valida campos obrigatórios (status, liga, série, etc)
  - Conta partidas por status (futuras, ao vivo, finalizadas, canceladas)
  - Verifica integridade de dados
- **Resultado**: Relatório de validação

**Exemplo de output:**
```
✅ Cache Validation Report
Total de partidas: 106
  - Futuras: 50
  - Ao vivo: 2
  - Finalizadas: 20
  - Canceladas: 20
  - Outras: 14

✅ Campos validados: 10/10
- Status ✓
- Liga ✓
- Série ✓
- Torneio ✓
- ... etc
```

---

### 3️⃣ **preview_embed.py** - Preview de Embeds
```bash
python scripts/preview_embed.py
```
- **Quando usar**: Ver como embeds ficam formatados no Discord
- **O que faz**: 
  - Busca partidas em cache
  - Formata embeds (como seriam no Discord)
  - Mostra preview em texto/JSON
- **Resultado**: Preview dos embeds

**Exemplo:**
```
Partida #1: SK vs FURIA
Status: Futura (em 2 horas)
🏆 Torneio: ESL Pro League Season 19
📍 Liga: INTEL EXTREME MASTERS
...
```

---

### 4️⃣ **check_api_structure.py** - Verificar Estrutura da API
```bash
python scripts/check_api_structure.py
```
- **Quando usar**: Debug de conexão com PandaScore
- **O que faz**:
  - Conecta na API PandaScore
  - Faz requisição de teste
  - Mostra estrutura de dados retornada
- **Resultado**: JSON com estrutura da API

---

### 5️⃣ **check_api_status_filter.py** - Testar Filtros de Status
```bash
python scripts/check_api_status_filter.py
```
- **Quando usar**: Verificar se API retorna dados por status
- **O que faz**:
  - Testa filtros: `finished`, `canceled`, `postponed`, `running`
  - Mostra quantas partidas retornam por cada filtro
  - Valida se dados estão corretos
- **Resultado**: Relatório de partidas por status

**Exemplo:**
```
Status: finished → 20 partidas
Status: canceled → 15 partidas
Status: postponed → 5 partidas
Status: running → 2 partidas
```

---

### 6️⃣ **check_api_past.py** - Verificar Partidas Passadas
```bash
python scripts/check_api_past.py
```
- **Quando usar**: Debug de partidas finalizadas
- **O que faz**:
  - Busca partidas finalizadas na API
  - Mostra detalhes (placar, mapas, etc)
  - Valida estrutura de dados
- **Resultado**: Lista de partidas finalizadas

---

### 7️⃣ **check_cache_content.py** - Ver Conteúdo do Cache
```bash
python scripts/check_cache_content.py
```
- **Quando usar**: Debug rápido do que está em cache
- **O que faz**:
  - Lista todas as partidas no banco
  - Mostra resumo de cada uma
  - Filtros por status
- **Resultado**: Dump do cache

---

### 8️⃣ **check_status.py** - Verificar Status Geral
```bash
python scripts/check_status.py
```
- **Quando usar**: Health check rápido do sistema
- **O que faz**:
  - Verifica conexão DB
  - Verifica conexão API
  - Conta partidas em cache
  - Resume estado geral
- **Resultado**: Status geral do sistema

**Exemplo:**
```
✅ Banco de dados: OK (106 partidas)
✅ API PandaScore: OK (token válido)
✅ Cache: OK (atualizado há 5 min)
⚠️ Notificações: 2 pendentes
```

---

### 9️⃣ **analyze_match_status.py** - Analisar Estados de Partidas
```bash
python scripts/analyze_match_status.py
```
- **Quando usar**: Entender distribuição de estados
- **O que faz**:
  - Analisa todos os estados de partidas
  - Mostra gráfico de distribuição
  - Identifica anomalias
- **Resultado**: Análise de estados

---

## 🚀 Como Usar

### Rodar um script
```bash
python scripts/nome_do_script.py
```

### Com argumentos (alguns scripts suportam)
```bash
python scripts/validate_cache_full.py --verbose
python scripts/preview_embed.py --match-id 12345
```

### Ver ajuda
```bash
python scripts/nome_do_script.py --help
```

---

## 🔍 Casos de Uso Comuns

### "Tudo tá funcionando?"
```bash
python scripts/check_status.py
```

### "Preciso ver como embeds ficam no Discord"
```bash
python scripts/preview_embed.py
```

### "Acho que cache está quebrado"
```bash
python scripts/validate_cache_full.py
```

### "API conecta?"
```bash
python scripts/check_api_structure.py
```

### "Por que faltam partidas finalizadas?"
```bash
python scripts/check_api_past.py
```

### "Quero debugar em detalhes"
```bash
python scripts/check_cache_content.py
python scripts/validate_cache_full.py --verbose
```

---

## 📊 Fluxo de Debug Recomendado

1. **Status geral**
   ```bash
   python scripts/check_status.py
   ```

2. **Se houver problema, verificar cache**
   ```bash
   python scripts/validate_cache_full.py
   ```

3. **Se problema for de dados, verificar API**
   ```bash
   python scripts/check_api_structure.py
   ```

4. **Se for de status específico, testar filtro**
   ```bash
   python scripts/check_api_status_filter.py
   ```

5. **Se for visual, preview dos embeds**
   ```bash
   python scripts/preview_embed.py
   ```

---

## 🎯 Scripts por Objetivo

### Verificar Integridade
- `validate_cache_full.py` - Validação completa
- `check_status.py` - Health check rápido

### Debugar Dados
- `check_cache_content.py` - Ver o que está em cache
- `check_api_structure.py` - Estrutura da API
- `check_api_past.py` - Partidas finalizadas

### Testar Features
- `preview_embed.py` - Como embeds ficam
- `analyze_match_status.py` - Análise de estados
- `check_api_status_filter.py` - Filtros de status

### Setup
- `init_db.py` - Inicializar banco (primeira vez)

---

## 💡 Dicas

- 🔄 Rodar `validate_cache_full.py` frequentemente para monitorar
- 📝 Logs estão em `logs/` para histórico de execução
- 🚨 Se algo falhar, verificar `.env` (token precisa ser válido)
- ⏱️ Cache atualiza a cada 15 minutos (5 min para live)

---

## 🆘 Se algo não funcionar

1. Verificar `.env` com tokens corretos
2. Rodar `python scripts/check_status.py`
3. Ver logs em `logs/`
4. Rodar `python scripts/validate_cache_full.py` para mais detalhes

---

**Status**: ✅ Scripts Operacionais  
**Versão**: 3.0  
**Data**: 2025-11-16
