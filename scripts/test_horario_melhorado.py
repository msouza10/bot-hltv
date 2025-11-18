#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do horário melhorado com dia da semana, data e timezone
"""

import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from src.utils.embeds import create_match_embed

# Dados de teste
match_data = {
    'id': 12345,
    'begin_at': '2025-11-18T20:00:00Z',
    'opponents': [
        {'name': 'Furia', 'image_url': None, 'acronym': 'FURIA'},
        {'name': 'Vitality', 'image_url': None, 'acronym': 'VIT'}
    ],
    'league': {'name': 'ESL Pro League', 'image_url': None},
    'tournament': {'name': 'ESL Pro League', 'prizepool': '500000'},
    'status': 'not_started'
}

print("=" * 70)
print("🧪 TESTE: Horário Melhorado com Dia da Semana, Data e Timezone")
print("=" * 70)

timezones = [
    'America/Sao_Paulo',
    'America/New_York',
    'Europe/London',
    'Asia/Tokyo'
]

for tz in timezones:
    print(f"\n📍 Testando: {tz}")
    try:
        embed = create_match_embed(match_data, timezone=tz)
        
        # Buscar o campo de horário
        for field in embed.fields:
            if field.name == "⏰ Horário":
                print(f"   ✅ Horário: {field.value}")
                break
        
        # Também mostrar footer
        if embed.footer:
            print(f"   📝 Footer: {embed.footer.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 70)
