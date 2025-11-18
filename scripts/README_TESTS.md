# 🧪 Scripts de Teste - YouTube Service

## Disponíveis

### 1. **test_youtube_service.py** - Teste de API

Testa o serviço YouTube com URLs públicas conhecidas (Rick Astley, etc).

```bash
python scripts/test_youtube_service.py
```

**O que testa:**
- ✅ URLs de vídeo (watch?v=...)
- ✅ URLs curtas (youtu.be/...)
- ✅ Fallback para handles (@)
- ✅ Fallback para custom URLs (c/)

**Resultado esperado:**
- 2/5 sucessos com API
- 3/5 sucessos com fallback
- Taxa de sucesso: 100%

---

### 2. **test_youtube_real_data.py** - Teste com Dados Reais

Busca URLs reais do banco de dados e testa a extração de nomes.

```bash
# Primeiro certifique-se de que o bot rodou e coletou dados
python -m src.bot  # Deixe rodando por alguns minutos
# Ctrl+C para parar

# Depois execute o teste
python scripts/test_youtube_real_data.py
```

**O que faz:**
- Conecta ao banco de dados
- Busca todos os streams do YouTube
- Testa extração de nome para cada um
- Mostra quais URLs deveriam ser atualizadas

**Exemplo de saída:**
```
[1/3] Match ID: 1269370
      URL: https://www.youtube.com/watch?v=CuHkkYAiPcM
      Canal atual no DB: YouTube
      🎥 Nome real obtido: ESL Counter-Strike
      ✅ DIFERENTE - Deveria ser atualizado
```

---

### 3. **run_complete_test.py** - Teste Completo Automático

Faz tudo automaticamente:
1. Reset do banco
2. Coleta dados do bot por 30 segundos
3. Executa teste com dados reais

```bash
python scripts/run_complete_test.py
```

**Tempo total:** ~35 segundos

**Resultado:**
- Mostra quantos streams foram coletados
- Lista URLs que precisam atualização
- Taxa de sucesso geral

---

## Setup Pré-requisitos

### 1. YouTube API Key

Obtenha em: https://console.cloud.google.com/

1. Crie um projeto
2. Ative "YouTube Data API v3"
3. Crie uma "API Key"
4. Adicione ao `.env`:

```bash
YOUTUBE_API_KEY=sua_chave_aqui
```

### 2. Banco de Dados

O banco será criado automaticamente, mas certifique-se de:

```bash
# Setup inicial
python -m src.database.build_db

# Verificar se banco existe
ls -lah data/bot.db
```

---

## Interpretando Resultados

### ✅ Sucesso
```
🎥 Nome real obtido: Team Liquid
✅ DIFERENTE - Deveria ser atualizado
```
Significa que conseguiu buscar o nome real da API e é diferente do que está no BD.

### ⚠️ Fallback
```
⚠️  Sem nome obtido (usando fallback)
```
A API não respondeu, mas o fallback pode ter extraído algo da URL.

### ❌ Falha
```
❌ ERRO: Connection timeout
```
Houve um erro e nem o fallback funcionou.

---

## Troubleshooting

### Erro: "No module named 'src'"
```bash
# Certifique-se de estar no diretório raiz
cd bot-hltv
python scripts/test_youtube_service.py
```

### Erro: "YOUTUBE_API_KEY não configurada"
```bash
# Copie .env.example
cp .env.example .env

# Adicione sua chave
echo "YOUTUBE_API_KEY=sua_chave" >> .env
```

### Erro: "No such file or directory: 'data/bot.db'"
```bash
# Initialize o banco
python -m src.database.build_db

# Ou rode o script completo que faz tudo
python scripts/run_complete_test.py
```

### Erro: "YouTube API limit exceeded"
Significa que excedeu a quota diária (10.000 unidades). Espere até amanhã.

---

## Entendendo a Saída

### test_youtube_service.py
```
✅ Passou:  2
❌ Falhou:  3
🎯 Taxa de sucesso: 40.0%
```
40% é o esperado (videos funcionam com API, canais usam fallback)

### test_youtube_real_data.py
```
[1/10] Match ID: 1269370
       🎥 Nome real obtido: ESL Counter-Strike
       ✅ DIFERENTE - Deveria ser atualizado
```
Significa que devemos atualizar o banco com o nome correto.

### run_complete_test.py
```
✅ Sucessos:  8
❌ Falhas:    2
🎯 Taxa de sucesso: 80.0%
```
Ótimo! A maioria dos streams conseguiu extrair o nome.

---

## Próximos Passos

1. ✅ Teste básico: `test_youtube_service.py`
2. ✅ Teste com dados reais: `test_youtube_real_data.py`
3. ✅ Teste completo: `run_complete_test.py`
4. 🚀 Deploy para produção

---

## Logs Detalhados

Se precisar ver logs mais detalhados durante os testes:

```bash
# Ativar debug mode
export LOG_LEVEL=DEBUG
python scripts/test_youtube_real_data.py
```

Procure por:
- `🎥 Nome do canal YouTube obtido via API`
- `⚠️ YouTube API Key não configurada`
- `❌ Erro ao buscar nome do canal`
