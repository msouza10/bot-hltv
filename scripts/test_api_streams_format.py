#!/usr/bin/env python3
"""
Test: Formatar streams que vêm direto da API (com streams_list)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.embeds import format_streams_field


def test_api_streams():
    """Test formatting streams que vêm da API"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Formatar streams que vêm da API")
    print("="*80 + "\n")
    
    # Simular streams_list como vem da API
    api_streams = [
        {
            "main": True,
            "language": "en",
            "embed_url": "https://player.kick.com/nodwin_cs2",
            "official": True,
            "raw_url": "https://kick.com/nodwin_cs2"
        },
        {
            "main": False,
            "language": "ru",
            "embed_url": "https://player.twitch.tv/?channel=sigmacast2",
            "official": False,
            "raw_url": "https://www.twitch.tv/sigmacast2"
        },
        {
            "main": False,
            "language": "tr",
            "embed_url": "https://player.twitch.tv/?channel=arhavalcom",
            "official": False,
            "raw_url": "https://www.twitch.tv/arhavalcom"
        }
    ]
    
    print(f"1️⃣  Streams da API (raw):\n")
    for i, s in enumerate(api_streams):
        print(f"   Stream {i}: {s}")
    
    print(f"\n2️⃣  Tentando formatar diretamente...")
    formatted = format_streams_field(api_streams)
    
    if formatted:
        print(f"   ✅ Resultado:")
        for line in formatted.split("\n"):
            print(f"      {line}")
    else:
        print(f"   ❌ Resultado: None (não conseguiu formatar!)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_api_streams()
