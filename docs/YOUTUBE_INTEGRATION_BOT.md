# 🎥 Integração YouTube no Bot

## Como Funciona

Toda vez que o bot cacheia um stream do YouTube, ele **automaticamente** extrai o nome real do canal e salva no banco de dados.

### Fluxo Completo

```text
1. API PandaScore retorna match com stream YouTube
   └─ URL: https://www.youtube.com/watch?v=CuHkkYAiPcM

2. Bot chama cache_scheduler.cache_matches()
   └─ Inicia processamento de streams

3. cache_manager.cache_streams() é acionado
   └─ Detecta que é YouTube
   └─ Chama YouTubeService.get_channel_name()

4. YouTubeService extrai o nome real
   └─ Se tem API Key: busca via API
   └─ Se não: usa fallback (extrai da URL)

5. Nome real é salvo no banco
   └─ channel_name = "ESL Counter-Strike" (em vez de "YouTube")

6. Log mostra a operação
   └─ 🎥 YouTube: 'YouTube' → 'ESL Counter-Strike' (Match 1269370)

7. Embed do Discord mostra nome correto
   └─ [ESL Counter-Strike](url) - 🇬🇧
```

---

## Logs Que Você Verá

### Sucesso com API

```log
🎥 YouTube: 'YouTube' → 'Team Liquid' (Match 1269370)
📡 1 stream(s) cacheado(s) para match 1269370 [PandaScore API]
```

### Sucesso com Fallback

```log
🎥 YouTube: 'live' → 'elisaesports' (Match 1253022)
📡 1 stream(s) cacheado(s) para match 1253022 [PandaScore API]
```

### Erro (continua funcionar com fallback)

```log
⚠️ Erro ao buscar nome do canal YouTube: Connection timeout
🎥 YouTube: 'YouTube' → 'YouTube' (usando fallback)
```

---

## Casos Cobertos

| Tipo de URL | Extração | Exemplo |
|-------------|----------|---------|
| `watch?v=VIDEO_ID` | API + Fallback | Busca o canal do vídeo |
| `youtu.be/VIDEO_ID` | API + Fallback | Busca o canal do vídeo |
| `@CHANNEL/live` | Fallback | Extrai: CHANNEL |
| `c/CHANNEL` | Fallback | Extrai: CHANNEL |
| `channel/CHANNEL_ID` | Fallback | Usa ID como nome |

---

## Configuração Necessária

### 1. YouTube API Key (opcional, mas recomendado)

Para obter nomes de vídeos corretamente, adicione ao `.env`:

```bash
YOUTUBE_API_KEY=sua_chave_aqui
```

### 2. Sem API Key

Funciona mesmo sem a chave usando fallback:

- URLs com `@` → extrai o handle
- URLs com `c/` → extrai o canal
- URLs com `watch?v=` → usa "YouTube" como nome

---

## Fluxo de Dados

```text
┌─────────────────────────────────────┐
│   API PandaScore                    │
│  (match com streams_list)           │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│   cache_scheduler.update_all_...()  │
│  (Task executada a cada 3 min)      │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  cache_manager.cache_matches()      │
│  (Processa cada match)              │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  cache_manager.cache_streams()      │
│  (Processa cada stream)             │
└──────────────┬──────────────────────┘
               │
               ├─ Se platform == "youtube"
               │
               ↓
┌─────────────────────────────────────┐
│  YouTubeService.get_channel_name()  │
│  (Extrai nome real do canal)        │
└──────────────┬──────────────────────┘
               │
         ┌─────┴──────────────┐
         │                    │
    ✅ Com API Key      ❌ Sem API Key
         │                    │
         ↓                    ↓
    API YouTube v3       Fallback
    videos.list()        (parse URL)
         │                    │
         └─────────┬──────────┘
                   │
                   ↓
         ┌──────────────────────┐
         │  Nome real do canal  │
         └──────────┬───────────┘
                    │
                    ↓
         ┌──────────────────────┐
         │  Salva no banco      │
         │  match_streams       │
         └──────────┬───────────┘
                    │
                    ↓
         ┌──────────────────────┐
         │  Exibe no Discord    │
         │  embed do match      │
         └──────────────────────┘
```

---

## Performance

- **Com API Key**: ~1 segundo por stream (requisição HTTP)
- **Sem API Key**: <10ms por stream (parse de URL)
- **Cache**: YouTube service mantém sessão persistente

As requisições são feitas **em paralelo** durante o processamento de múltiplos streams, então não há bloqueio.

---

## Monitoramento

### Verificar Logs

```bash
# Ver todos os logs do YouTube
tail -f logs/bot.log | grep -i "youtube"

# Ver só sucessos
tail -f logs/bot.log | grep "🎥"

# Ver só erros
tail -f logs/bot.log | grep "⚠️" | grep youtube
```

### Verificar Banco

```bash
# Ver streams do YouTube com nomes atualizados
sqlite3 data/bot.db "SELECT match_id, channel_name, raw_url FROM match_streams WHERE platform='youtube' LIMIT 5;"
```

### Exemplo de Saída

```text
1253022|elisaesports|https://www.youtube.com/@elisaesports/live
1269370|ESL Counter-Strike|https://www.youtube.com/watch?v=CuHkkYAiPcM
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Nomes ainda mostram "YouTube" | Adicione `YOUTUBE_API_KEY` no `.env` |
| Erro "YouTube API Key not found" | É normal, usa fallback automaticamente |
| Nomes não aparecem nos embeds | Aguarde o bot processar (próxima coleta em 3 min) |
| Quota API excedida | Espere até amanhã (10k unidades/dia) |

---

## Fórmula de Sucesso

```
✅ Bot rodando
✅ PandaScore API retornando dados
✅ YouTube API Key configurada (ou fallback ativo)
─────────────────────────────────
✅ Nomes reais de canais nos embeds
```

---

## Próximas Melhorias (Futuro)

- [ ] Cache persistente de nomes (não re-buscar)
- [ ] Sincronização periódica (atualizar nomes que mudaram)
- [ ] UI command para forçar atualização: `/update-youtube-names`
- [ ] Estatísticas: quantos canais foram atualizados
- [ ] Webhook para notificar mudanças de nome

---

## Referências

- [`src/services/youtube_service.py`](../src/services/youtube_service.py) - Implementação completa
- [`src/database/cache_manager.py`](../src/database/cache_manager.py) - Integração no bot
- [YouTube Data API v3 Docs](https://developers.google.com/youtube/v3)
