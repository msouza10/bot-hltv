#!/usr/bin/env python3
"""
Test extraction functions directly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager


def test_extraction():
    """Test _extract_platform e _extract_channel_name"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Extração de platform e channel_name")
    print("="*80 + "\n")
    
    test_urls = [
        "https://www.twitch.tv/sigmacast2",
        "https://www.twitch.tv/arhavalcom",
        "https://kick.com/nodwin_cs2",
        "https://youtube.com/@channel_name",
        "https://facebook.com/page_name",
    ]
    
    for url in test_urls:
        platform = MatchCacheManager._extract_platform(url)
        channel_name = MatchCacheManager._extract_channel_name(url)
        
        print(f"URL: {url}")
        print(f"  Platform: {platform}")
        print(f"  Channel: {channel_name}")
        print()
    
    print("="*80 + "\n")


if __name__ == "__main__":
    test_extraction()
