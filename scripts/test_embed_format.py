#!/usr/bin/env python3
"""Test embed format after changes"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

import nextcord
from datetime import datetime

# Simular create_match_embed
match_data = {
    'id': 123456,
    'status': 'running',
    'opponents': [
        {
            'opponent': {
                'id': 1,
                'name': 'Eternal Fire',
                'image_url': 'https://...'
            }
        },
        {
            'opponent': {
                'id': 2,
                'name': 'MANA eSports',
                'image_url': 'https://...'
            }
        }
    ],
    'league': {
        'name': 'NODWIN Clutch Series',
        'id': 99
    },
    'serie': {
        'full_name': 'Season 3 2025',
        'name': 'Season 3 2025',
        'id': 88
    },
    'tournament': {
        'name': 'NODWIN Clutch Series',
        'id': 99
    },
    'number_of_games': 3,
    'scheduled_at': '2025-11-17T15:00:00Z',
    'results': [
        {'score': 1},
        {'score': 0}
    ],
    'formatted_streams': 'Twitch\n└ sigmacast2 - 🇷🇺\n└ arhavalcom - 🇷🇺\nKick\n└ nodwin_cs2 - 🇬🇧 -⭐'
}

# Criar embed manualmente para testar
embed = nextcord.Embed(
    title="🔴 Eternal Fire vs MANA eSports",
    color=0xe74c3c,
    timestamp=datetime.utcnow()
)

embed.add_field(name="🏆 Torneio", value="NODWIN Clutch Series", inline=False)
embed.add_field(name="📍 Série", value="Season 3 2025", inline=False)
embed.add_field(name="📺 Formato", value="BO3 - Best Of", inline=True)
embed.add_field(name="📊 Status", value="Running", inline=True)
embed.add_field(name="⏰ Horário", value="segunda-feira, 17 de novembro de 2025 às 15:00", inline=False)
embed.add_field(name="📡 Streams", value="**Twitch**\n└ [sigmacast2](https://www.twitch.tv/sigmacast2) - 🇷🇺\n└ [arhavalcom](https://www.twitch.tv/arhavalcom) - 🇷🇺\n**Kick**\n└ [nodwin_cs2](https://kick.com/nodwin_cs2) - 🇬🇧 -⭐", inline=False)

print("=" * 80)
print("📺 NOVO FORMATO DO EMBED")
print("=" * 80)
print()
for field in embed.fields:
    print(f"{field.name}")
    for line in field.value.split('\n'):
        print(f"  {line}")
    print()
print("=" * 80)
