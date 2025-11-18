# Fix: raw_url vs embed_url Bug

**Data**: 2025-01-18  
**Status**: ✅ CORRIGIDO  
**Severidade**: 🔴 CRÍTICO (Links quebrados)

---

## 🐛 O Problema

Ao clicar em um link de stream no Discord, o usuário recebia este erro:

```
https://player.twitch.tv/embed-error.html?errorCode=NoParent&content=player.twitch.tv%2F%3Fchannel%3Ddust2tv
```

**Causa**: O código estava usando `embed_url` quando `raw_url` não estava disponível.

---

## ❌ O Erro

Em `src/utils/embeds.py` linha 440:

```python
# ❌ INCORRETO
raw_url = stream.get("raw_url") or stream.get("embed_url", "")
```

### Por que isso era errado?

A API PandaScore fornece 2 tipos de URL para cada stream:

1. **`raw_url`** - URL direta do stream (ex: `https://twitch.tv/dust2tv`)
   - ✅ Funciona para cliques diretos no Discord
   - ✅ URL navegável

2. **`embed_url`** - URL de embed do Twitch (ex: `https://player.twitch.tv/embed?channel=dust2tv`)
   - ✗ Não funciona como link clicável
   - ✗ Retorna erro se visitado diretamente: `embed-error.html?errorCode=NoParent`

### Fluxo do Bug

```
Stream sem raw_url
    ↓
Código usa fallback: stream.get("raw_url") or stream.get("embed_url", "")
    ↓
embed_url é escolhido (porque raw_url é None/vazio)
    ↓
Discord hyperlink aponta para embed_url
    ↓
Usuário clica → https://player.twitch.tv/embed-error.html (erro!)
```

---

## ✅ A Solução

```python
# ✅ CORRETO
raw_url = stream.get("raw_url", "")
if raw_url:
    # Usar raw_url
    ...
```

### Novo Fluxo

```
Stream recebido
    ↓
Verificar raw_url
    ↓
if raw_url:
    - Extrair platform e channel_name
    - Usar raw_url para hyperlink
else:
    - Usar platform="other", channel_name="Unknown"
    - Sem hyperlink (link quebrado não existe)
```

---

## 📝 Mudança no Código

**Arquivo**: `src/utils/embeds.py`  
**Linha**: 440

### Antes (❌ bug)
```python
raw_url = stream.get("raw_url") or stream.get("embed_url", "")
```

### Depois (✅ correto)
```python
raw_url = stream.get("raw_url", "")
```

---

## 🔍 Verificação

**Cenário 1: Stream com raw_url**
```
Input: {
    "raw_url": "https://twitch.tv/dust2tv",
    "embed_url": "https://player.twitch.tv/...",
    "language": "pt"
}

Output: [dust2tv](https://twitch.tv/dust2tv) - 🇵🇹
✅ Link funciona!
```

**Cenário 2: Stream sem raw_url** (era o bug)
```
Input: {
    "embed_url": "https://player.twitch.tv/embed-error.html?...",
    "language": "pt"
}

❌ ANTES: Usava embed_url → Erro ao clicar
✅ DEPOIS: Não usa nada → Sem hyperlink, mas sem erro
```

---

## 🎯 Impacto

### Antes
```
Stream clicável, mas quebrado
└ user clica → https://player.twitch.tv/embed-error.html
```

### Depois
```
Stream sem raw_url = sem hyperlink (não quebra mais)
Stream com raw_url = hyperlink direto funciona
```

---

## 📚 Referência

**Campos da API PandaScore**:
- `raw_url`: URL direta (Twitch, Kick, YouTube, etc)
- `embed_url`: URL de embed (apenas para embeds no Discord/web)
- `language`: ISO 639-1 (pt, en, ru, etc)
- `official`: boolean
- `main`: boolean

**Nunca misture**:
- ❌ `embed_url` para links clicáveis
- ✅ `raw_url` para links clicáveis

---

## 🟢 Status

✅ **Corrigido**  
✅ **Testado**  
✅ **Pronto para produção**

Links de streams agora funcionam corretamente quando:
1. `raw_url` está disponível (a maioria dos casos)
2. Quando `raw_url` não existe, não há hiperlink (melhor que erro)
