#!/usr/bin/env python3
"""
Script para testar embeds sem rodar o bot
"""
import sys
sys.path.insert(0, '.')

import sqlite3
import json
import nextcord
from src.utils.embeds import create_result_embed

conn = sqlite3.connect('data/bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Buscar uma partida finalizada
c.execute('SELECT match_data FROM matches_cache WHERE status = "finished" LIMIT 1')
row = c.fetchone()

if row:
    match_data = json.loads(row['match_data'])
    embed = create_result_embed(match_data)
    
    print("\n" + "="*80)
    print("PREVIEW DO EMBED")
    print("="*80)
    
    print(f"\nTITULO: {embed.title}")
    print(f"DESCRICAO: {embed.description}")
    print(f"\nCAMPOS:")
    
    for field in embed.fields:
        print(f"\n[{field.name}]")
        # Limitar a 100 chars por linha para preview
        lines = field.value.split('\n')
        for line in lines[:5]:
            if len(line) > 100:
                print(f"  {line[:100]}...")
            else:
                print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... (+{len(lines)-5} linhas)")
    
    if embed.thumbnail:
        print(f"\nTHUMBNAIL: {embed.thumbnail.url[:60]}..." if len(embed.thumbnail.url) > 60 else f"\nTHUMBNAIL: {embed.thumbnail.url}")
    
    print(f"\nCOR: #{embed.colour:06x}")
    print(f"FOOTER: {embed.footer.text if embed.footer else 'N/A'}")
    
    print("\n" + "="*80)
else:
    print("Nenhuma partida encontrada")

conn.close()
