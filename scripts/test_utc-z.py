import sys
import os
from datetime import datetime
# Ajusta path para importar src como módulo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.utils.embeds import create_match_embed
# Caso TimezoneManager/embeds necessitem de dependências extras:
# from src.utils.timezone_manager import TimezoneManager

# Exemplo simplificado de match_data com begin_at em UTC
match_data = {
    "id": 12345,
    "status": "not_started",
    "scheduled_at": "2025-11-20T19:11:00Z",
    "begin_at": "2025-11-20T19:11:00Z",
    "opponents": [
        {"opponent": {"name": "Team Alpha", "image_url": None}},
        {"opponent": {"name": "Team Beta", "image_url": None}},
    ],
    "league": {"name": "DreamLeague", "image_url": None},
    "serie": {"full_name": "Series X"},
    "tournament": {"name": "DreamHack", "tier": "premier", "region": "sa", "type": "offline"},
    "formatted_streams": []
}

timezones_to_test = [
    "America/Sao_Paulo",  # Brazil - BRT (UTC-3)
    "Europe/London",      # GMT (UTC+0)
    "Asia/Tokyo",         # JST (UTC+9)
    "America/New_York",   # EST (UTC-5)
    "UTC"
]

for tz in timezones_to_test:
    embed = create_match_embed(match_data, timezone=tz)
    data = embed.to_dict()
    footer_text = data.get("footer", {}).get("text", "")
    fields = {f["name"]: f["value"] for f in data.get("fields", [])}
    horario_field = fields.get("⏰ Horário") or fields.get("Horario") or fields.get("⏰ Horário agendado")
    ts = embed.timestamp
    unix_ts = int(ts.timestamp()) if ts else None

    print("------------------------------------------------------------")
    print(f"Time zone test: {tz}")
    print(f"Footer: {footer_text}")
    print(f"Horário field: {horario_field}")
    if unix_ts:
        print(f"Discord dynamic timestamp (full): <t:{unix_ts}:f>")
        print(f"Discord dynamic timestamp (short): <t:{unix_ts}:R>")
    print("------------------------------------------------------------\n")