#!/usr/bin/env python3
"""
Test /aovivo command with actual stream formatting
Simulates what happens when user calls /aovivo command
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import create_match_embed, augment_match_with_streams


async def test_aovivo_formatting():
    """Test formatting /aovivo matches with stream display"""
    
    print("=" * 80)
    print("🧪 TEST: /aovivo Formatting with Real Streams")
    print("=" * 80)
    print()
    
    # Initialize cache manager
    cache_manager = MatchCacheManager(db_url="file:./data/bot.db")
    
    try:
        # Get running matches
        print("1️⃣  Fetching RUNNING matches from cache...")
        running_matches = await cache_manager.get_cached_matches("running", 5)
        
        if not running_matches:
            print("   ❌ No running matches in cache")
            return
        
        print(f"   ✅ Found {len(running_matches)} running match(es)")
        print()
        
        # Get streams for each match
        print("2️⃣  Augmenting matches with streams...")
        augmented_matches = []
        for match in running_matches:
            try:
                augmented = await augment_match_with_streams(
                    match, 
                    cache_manager,
                    timeout=3.0
                )
                augmented_matches.append(augmented)
                print(f"   ✅ Match {match['id']}: augmented")
            except Exception as e:
                print(f"   ❌ Match {match['id']}: {type(e).__name__}: {e}")
        
        print()
        
        # Create embeds
        print("3️⃣  Creating Discord embeds...")
        for i, match in enumerate(augmented_matches[:3], 1):  # Show first 3
            try:
                embed = create_match_embed(match, status="running")
                print(f"\n   📊 Match {i}:")
                print(f"      Title: {embed.title}")
                
                # Extract streams field from embed
                for field in embed.fields:
                    if "stream" in field.name.lower() or "transmiss" in field.name.lower():
                        print(f"      Streams:")
                        lines = field.value.split("\n")
                        for line in lines:
                            print(f"         {line}")
                
            except Exception as e:
                print(f"   ❌ Embed {i}: {type(e).__name__}: {e}")
        
        print()
        print("=" * 80)
        print("✅ TEST COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cache_manager.close()


if __name__ == "__main__":
    asyncio.run(test_aovivo_formatting())
