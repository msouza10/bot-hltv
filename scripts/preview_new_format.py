#!/usr/bin/env python3
"""
Test visual preview of the new stream formatting in Discord embed
"""

import nextcord
from datetime import datetime
from src.utils.embeds import format_streams_field

# Simular streams da API
api_streams = [
    {
        'main': True,
        'language': 'en',
        'embed_url': 'https://player.kick.com/nodwin_cs2',
        'official': True,
        'raw_url': 'https://kick.com/nodwin_cs2'
    },
    {
        'main': False,
        'language': 'ru',
        'embed_url': 'https://player.twitch.tv/?channel=sigmacast2',
        'official': False,
        'raw_url': 'https://www.twitch.tv/sigmacast2'
    },
    {
        'main': False,
        'language': 'ru',
        'embed_url': 'https://player.twitch.tv/?channel=arhavalcom',
        'official': False,
        'raw_url': 'https://www.twitch.tv/arhavalcom'
    },
]

# Formatar
formatted_streams = format_streams_field(api_streams)

# Criar embed de exemplo
embed = nextcord.Embed(
    title="🔴 Eternal Fire vs MANA eSports",
    description="",
    color=nextcord.Color.red()
)

embed.add_field(
    name="🏆 Torneio",
    value="NODWIN Clutch Series",
    inline=False
)

embed.add_field(
    name="📍 Série",
    value="Season 3 2025",
    inline=False
)

embed.add_field(
    name="📺 Formato",
    value="BO3 - Best OF",
    inline=False
)

embed.add_field(
    name="📊 Status",
    value="Running",
    inline=False
)

embed.add_field(
    name="⏰ Horário",
    value="segunda-feira, 17 de novembro de 2025 às 15:00",
    inline=False
)

if formatted_streams:
    embed.add_field(
        name="📡 Streams",
        value=formatted_streams,
        inline=False
    )

# Print
print("=" * 80)
print("📺 PREVIEW DO EMBED COM NOVO FORMATO DE STREAMS")
print("=" * 80)
print()
print(f"✅ Título: {embed.title}")
print()

for field in embed.fields:
    print(f"{field.name}")
    for line in field.value.split('\n'):
        print(f"  {line}")
    print()

print("=" * 80)
