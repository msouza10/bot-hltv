# 🔍 Análise: API Twitch - Por que a busca não encontra os streams

## Problema Identificado

Você está procurando por "CCT Europe Betera Esports Leo Team" mas a API Twitch não retorna esses resultados, mesmo sendo visíveis na interface do site.

## Causas Raiz (Descobertas da Documentação Oficial)

### 1. **A API Twitch tem dois tipos de busca DIFERENTES:**

#### `GET /search/streams` (DESATUALIZADO ❌)
- Este endpoint faz busca full-text por query
- **NÃO INDEXA EM TEMPO REAL** - há latência entre o stream começar e aparecer na busca
- Resultados são baseados em indexação de mecanismo de busca
- Podem não incluir streams muito recentes

#### `GET /streams` (RECOMENDADO ✅)
- Retorna streams **ativos agora** ordenados por viewers
- Suporta filtros estruturados:
  - `game_id` - ID do jogo específico
  - `language` - Idioma do stream  
  - `user_id` / `user_login` - Streams de usuário específico
  - `tag_id` - Tags aplicadas ao stream
- **Esses filtros retornam dados em tempo real!**

### 2. **O Problema Real: Você está usando `/search/streams`** 

O código atual está fazendo:
```
GET https://api.twitch.tv/helix/streams?query=CCT Europe
```

Mas isso é uma busca TEXTUAL que depende de indexação, não uma busca estruturada!

### 3. **Streams de "CCT Europe" podem estar**

Opções mais prováveis:
- **Classificadas na categoria "Counter-Strike" (game_id=32399)**, não em uma categoria "CCT Europe"
- **Feitas por usuários/canais específicos** que fazem transmissões profissionais
- **Usando tags como "esports", "cs2", "cct"** ao invés de "CCT Europe"

## ✅ Solução Correta

### Estratégia 1: Busca por Categoria + Scoring
```python
# Usar /streams com game_id para Counter-Strike
GET /helix/streams?game_id=32399&first=50&language=pt

# Depois filtrar os resultados em código por título/tags
# com scoring de campeonato/times
```

### Estratégia 2: Busca por Canal Específico (Se souber o username)
```python
# Se a ESL, ESL Pro League, etc têm canais:
GET /helix/streams?user_id=ESPL_ID&first=50

# Ou procurar o stream pelo nome do broadcaster
GET /helix/channels?broadcaster_login=esplprostream
```

### Estratégia 3: Usar Tags
```python
# Se "esports" ou "cct" são tags:
# Primeiro pegar tag_id:
GET /helix/search/categories?query=esports

# Depois filtrar:
GET /helix/streams?tag_id=TAG_ID&game_id=32399
```

## 📊 Dados Documentados da API

Da documentação oficial:

**GET /streams Parameters:**
- `game_id` - Filter by game ID (max 10 IDs, reduced from 100)
- `language` - Filter by language code (e.g., "pt", "en")
- `user_id` - Filter by user ID (up to 100)
- `user_login` - Filter by login name (up to 100)
- `first` - Max results (default 20, max 100)
- `after` - Pagination cursor

**Response includes:**
- `id`, `user_id`, `user_login`, `user_name`
- `game_id`, `game_name` 
- `type` (always "live" for active)
- `title`, `viewer_count`, `started_at`
- `language`, `thumbnail_url`
- `tags` - Array of tag objects!

## 🎯 Por que "Counter-Strike 2" não funciona

- A documentação mostra que `game_id=32399` é para "Counter-Strike" genérico
- Não existe um game_id específico para "Counter-Strike 2" na API atualmente
- ID 32399 retorna TODOS os streams de CS (CS1.6, CSGO, CS2, etc)

## Recomendação para o Bot

**Usar esta estratégia em ordem:**

1. **Busca Específica (Best):**  
   `GET /helix/streams?game_id=32399&first=50` + score por título

2. **Busca por Usuário/Canal (Se temos canal do ESL):**  
   `GET /helix/streams?user_login=esl` + search em tempo real

3. **Fallback: Tags + Categoria:**  
   Se houver tags "esports" ou "competitive", usar essas

4. **Último recurso: Search (Lento):**  
   `GET /helix/search/channels?query=CCT+Europe` para encontrar canal, depois buscar streams do canal

## Conclusão

**Você TEM RAZÃO!** Não é um comportamento correto. A API está indexando palavras-chave de forma inconsistente. 

A solução é **usar filtros estruturados** (`game_id`, `user_id`, `language`) ao invés de depender da busca textual, que depende de indexação em segundo plano.
