#!/usr/bin/env python3
"""
Quick validation script for timezone abbreviation and UTC offset format.

Usage:
    source venv/bin/activate
    python scripts/test_utc_z.py
"""
import sys
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.utils.timezone_manager import TimezoneManager
from src.utils.embeds import create_match_embed


def test_timezone(tz, expected_abbr=None, expected_offset=None):
    abbr = TimezoneManager.get_timezone_abbreviation(tz)
    offset = TimezoneManager.get_timezone_offset(tz)

    print(f"Testing {tz}: abbr={abbr}, offset={offset}")
    if expected_abbr:
        assert abbr == expected_abbr, f"Abbreviation mismatch for {tz}: {abbr} != {expected_abbr}"
    if expected_offset:
        assert offset.startswith(expected_offset), f"Offset mismatch for {tz}: {offset} != {expected_offset}"


def embed_check(tz):
    sample = {
        "id": 12345,
        "status": "not_started",
        "scheduled_at": "2025-11-20T19:11:00Z",
        "begin_at": "2025-11-20T19:11:00Z",
        "opponents": [
            {"opponent": {"name": "Team Alpha"}},
            {"opponent": {"name": "Team Beta"}}
        ],
        "league": {"name": "TestLeague"},
        "serie": {"full_name": "Series X"},
        "tournament": {"name": "Tourney"}
    }
    embed = create_match_embed(sample, timezone=tz)
    footer = embed.footer.text if embed.footer else ""
    horario = None
    for f in embed.fields:
        if f.name == "⏰ Horário":
            horario = f.value
            break

    print(f"Embed Footer: {footer}")
    print(f"Horário: {horario}")
    assert footer and "PandaScore API" in footer, "Footer missing or malformed"
    assert horario, "Horário field missing"


if __name__ == "__main__":
    tests = [
        ("America/Sao_Paulo", "BRT", "UTC-3"),
        ("America/New_York", "EST", "UTC-5"),
        ("Europe/London", "GMT", "UTC+0"),
        ("Asia/Tokyo", "JST", "UTC+9"),
        ("UTC", "UTC", "UTC+0"),
    ]

    for tz, abbr, off in tests:
        test_timezone(tz, abbr, off)
        embed_check(tz)

    print("All timezone checks passed")
