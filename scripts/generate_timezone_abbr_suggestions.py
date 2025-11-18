#!/usr/bin/env python3
"""
Gera sugestões de abreviações para timezones não mapeados em `TIMEZONE_ABBREVIATIONS`.

Usa heurística simples:
 - Se `tzname` em 1 Jan e 1 Jul for igual e textual, usa essa abreviação.
 - Se forem diferentes, sugere objeto {std: abbr_jan, dst: abbr_jul}.
 - Se tzname for um offset ("-03"), gera fallback usando "UTC±N" com horas/minutos.

Executar:
    source venv/bin/activate
    python scripts/generate_timezone_abbr_suggestions.py
"""
from datetime import datetime
import pytz
import json
import sys
from typing import Dict

ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.utils.timezone_manager import TIMEZONE_ABBREVIATIONS


def tz_tzname_for_date(tz_name: str, year: int, month: int, day: int):
    tz = pytz.timezone(tz_name)
    # Use localize to avoid ambiguous aware dt
    dt_naive = datetime(year, month, day, 12, 0, 0)
    try:
        dt_local = tz.localize(dt_naive, is_dst=None)
    except Exception:
        # Fallback: interpret as UTC then convert
        dt_local = dt_naive.replace(tzinfo=pytz.UTC).astimezone(tz)
    name = dt_local.tzname() or ""
    return name, dt_local


def format_fallback_utc_offset(dt_local) -> str:
    try:
        offset = dt_local.utcoffset()
        if offset is None:
            return "UTC+0"
        total_seconds = int(offset.total_seconds())
        hours = total_seconds // 3600
        minutes = (abs(total_seconds) % 3600) // 60
        sign = "+" if hours >= 0 else "-"
        if minutes:
            return f"UTC{sign}{abs(hours)}:{minutes:02d}"
        else:
            return f"UTC{sign}{abs(hours)}"
    except Exception:
        return "UTC+0"


def is_offset_token(token: str) -> bool:
    if not token:
        return True
    return token.startswith("+") or token.startswith("-") or token.upper().startswith("UTC")


def main():
    now = datetime.utcnow()
    suggestions: Dict[str, object] = {}

    existing = set(TIMEZONE_ABBREVIATIONS.keys())

    for tz in pytz.all_timezones:
        if tz in existing:
            continue
        # Skip weird entries
        if tz.startswith("ETC/"):
            continue

        jan_name, jan_dt = tz_tzname_for_date(tz, 2025, 1, 1)
        jul_name, jul_dt = tz_tzname_for_date(tz, 2025, 7, 1)

        # Both offsets?
        jan_is_offset = is_offset_token(jan_name)
        jul_is_offset = is_offset_token(jul_name)

        if jan_name == jul_name and not jan_is_offset:
            # Single abbreviation
            suggestions[tz] = jan_name
        elif jan_name != jul_name and not jan_is_offset and not jul_is_offset:
            suggestions[tz] = {"std": jan_name, "dst": jul_name}
        else:
            # fallback to UTC offset representation using jan or jul (choose current month near now)
            try:
                dt_local = tz.localize(now.replace(tzinfo=None))
            except Exception:
                dt_local = now.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(tz))
            offset = format_fallback_utc_offset(dt_local)
            suggestions[tz] = offset

    # Print result in python dict format sorted by timezone
    print("# Suggestions for TIMEZONE_ABBREVIATIONS (paste into timezone_manager.py)")
    print("# Format: 'Region/Location': 'ABBR' or 'Region/Location': { 'std':'STD', 'dst':'DST' }")
    print("{")
    for tz in sorted(suggestions.keys()):
        v = suggestions[tz]
        if isinstance(v, dict):
            print(f"    \"{tz}\": {{\"std\": \"{v['std']}\", \"dst\": \"{v['dst']}\"}},")
        else:
            print(f"    \"{tz}\": \"{v}\",")
    print("}")


if __name__ == '__main__':
    main()
