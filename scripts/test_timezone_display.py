#!/usr/bin/env python3
"""
Script para testar e visualizar timezone sendo usado.
Este script mostra exatamente qual timezone está sendo respeitado para o servidor.
"""

import asyncio
import json
import logging
from datetime import datetime

# Configurar logging para ver os mensagens de timezone
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("TIMEZONE TEST - Verificando qual timezone está sendo usado")
print("=" * 80)
print()

async def test_timezone():
    """Teste simples para mostrar qual timezone está configurado."""
    
    print("📍 Timezone no servidor:")
    print("-" * 80)
    
    # Importar TimezoneManager
    from src.utils.timezone_manager import TimezoneManager
    
    # Testar com alguns timezones
    test_timezones = [
        "America/Sao_Paulo",      # Brasil (padrão)
        "America/New_York",       # EUA
        "Europe/London",          # UK
        "Asia/Tokyo",             # Japão
        "Australia/Sydney",       # Austrália
    ]
    
    # ISO string de teste (2025-01-15 18:00:00 UTC)
    test_iso = "2025-01-15T18:00:00Z"
    
    print(f"\nTestando conversão de: {test_iso} (UTC)")
    print()
    
    for tz in test_timezones:
        try:
            dt_utc = TimezoneManager.parse_iso_datetime(test_iso)
            timestamp = TimezoneManager.discord_timestamp(dt_utc, tz)
            abbr = TimezoneManager.get_timezone_abbreviation(tz)
            offset = TimezoneManager.get_timezone_offset(tz)
            
            print(f"🌍 {tz}")
            print(f"   Discord Timestamp: {timestamp}")
            print(f"   Abreviação: {abbr}")
            print(f"   Offset UTC: {offset}")
            print()
        except Exception as e:
            print(f"❌ Erro com {tz}: {e}")
            print()
    
    print("=" * 80)
    print("✅ Para ver qual timezone está sendo usado em tempo real:")
    print("   1. Inicie o bot: venv/bin/python -m src.bot")
    print("   2. Use /partidas, /aovivo ou /resultados")
    print("   3. Veja nos logs: logs/bot.log")
    print("   4. Procure por: '🌍 /partidas: Timezone do servidor ='")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_timezone())
