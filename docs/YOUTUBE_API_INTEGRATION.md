# YouTube Data API v3 Integration

## Objetivo

Extrair automaticamente o nome real do canal/streamer a partir de URLs do YouTube usando a YouTube Data API v3.

## Como Funciona

1. **Detecção de URL do YouTube**: Quando um stream do YouTube é cacheado, o sistema identifica o tipo de URL:
   - `youtube.com/watch?v=VIDEO_ID` → Busca o canal do vídeo
   - `youtu.be/VIDEO_ID` → Busca o canal do vídeo
   - `youtube.com/@CHANNEL_NAME` → Busca pelo handle
   - `youtube.com/c/CHANNEL_NAME` → Busca pela custom URL
   - `youtube.com/channel/CHANNEL_ID` → Busca pelo ID do canal

2. **Chamada à API v3**: O serviço envia uma requisição para a YouTube Data API v3 com o identificador apropriado

3. **Cache e Armazenamento**: O nome do canal é armazenado no banco de dados e usado nos embeds

## Setup

### 1. Gerar YouTube API Key

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou use um existente
3. Ative a **YouTube Data API v3**:
   - Vá para APIs & Services > Library
   - Procure por "YouTube Data API v3"
   - Clique em "Enable"
4. Crie credenciais:
   - Vá para APIs & Services > Credentials
   - Clique em "Create Credentials"
   - Selecione "API Key"
   - Copie a chave gerada

### 2. Configurar no .env

Adicione a chave ao arquivo `.env`:

```bash
YOUTUBE_API_KEY=sua_youtube_api_key_aqui
```

## Fluxo de Funcionamento

### Quando um stream YouTube é cacheado:

```
1. Stream da API PandaScore chega com URL: https://www.youtube.com/watch?v=CuHkkYAiPcM
2. Sistema identifica que é YouTube
3. Extrai o Video ID: CuHkkYAiPcM
4. Chama YouTube Data API v3 para buscar o canal do vídeo
5. Recebe o nome real: "Team Liquid"
6. Armazena no banco: channel_name = "Team Liquid"
7. Exibe no embed do Discord:
   └ [Team Liquid](https://www.youtube.com/watch?v=CuHkkYAiPcM) - 🇬🇧
```

## Fallback

Se a YouTube API não estiver configurada ou retornar erro, o sistema faz um fallback:

- Tenta extrair direto da URL o handle ou custom URL
- Se não conseguir, usa "YouTube" como nome genérico

Exemplo de fallback:

```
youtube.com/@nisesports/live → Extrai: nisesports
youtube.com/c/espn → Extrai: espn
```

## Limites da API

A YouTube Data API v3 tem limites de quota:

- **Quota padrão**: 10.000 unidades por dia
- **Custo por tipo de requisição**:
  - Videos.list: 1 unidade
  - Channels.list: 1 unidade
  - Search: 100 unidades

Como usamos apenas `videos.list` e `channels.list`, o custo é mínimo:
- ~1 unidade por stream YouTube processado
- Com 10.000 unidades, podemos processar ~10.000 streams por dia

## Logs

O sistema registra informações úteis para debugar:

```
🎥 Nome do canal YouTube obtido via API: Team Liquid
📡 Match 1269370: youtube / Team Liquid (en) [PandaScore API]
```

Se houver erro:

```
⚠️ YouTube API Key não configurada, usando fallback para URL: ...
❌ Erro ao buscar nome do canal YouTube: ...
```

## Exemplos de URLs Suportadas

| URL | Tipo | Identificador |
|-----|------|---------------|
| `youtube.com/watch?v=dQw4w9WgXcQ` | Vídeo | Video ID |
| `youtu.be/dQw4w9WgXcQ` | Vídeo curto | Video ID |
| `youtube.com/@RickAstley` | Handle | @RickAstley |
| `youtube.com/@RickAstley/live` | Live do canal | @RickAstley |
| `youtube.com/c/RickAstley` | Custom URL | Custom URL |
| `youtube.com/channel/UCuAXFkgsw1L7xaCfnd5J-xQ` | Channel ID | Channel ID |

## Testando Localmente

Você pode testar o serviço com:

```python
import asyncio
from src.services.youtube_service import get_youtube_service

async def test():
    service = get_youtube_service()
    
    # Testar com URL de vídeo
    name = await service.get_channel_name("https://www.youtube.com/watch?v=CuHkkYAiPcM")
    print(f"Canal: {name}")
    
    # Testar com URL de canal
    name = await service.get_channel_name("https://www.youtube.com/@TeamLiquid")
    print(f"Canal: {name}")
    
    await service.close()

asyncio.run(test())
```

## Referências

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3/docs)
- [API Quotas and Rate Limits](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Channel Resource](https://developers.google.com/youtube/v3/docs/channels)
- [Video Resource](https://developers.google.com/youtube/v3/docs/videos)
