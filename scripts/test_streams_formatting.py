#!/usr/bin/env python3
"""
Test with upcoming matches that have streams
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import create_match_embed, augment_match_with_streams


async def test_upcoming_streams():
    """Test formatting upcoming matches with stream display"""
    
    print("=" * 80)
    print("🧪 TEST: /partidas Formatting with Real Streams")
    print("=" * 80)
    print()
    
    # Initialize cache manager
    cache_manager = MatchCacheManager(db_url="file:./data/bot.db")
    
    try:
        # Get upcoming matches
        print("1️⃣  Fetching UPCOMING matches from cache...")
        upcoming_matches = await cache_manager.get_cached_matches("not_started", 10)
        
        if not upcoming_matches:
            print("   ❌ No upcoming matches in cache")
            print("\n   💡 Trying to refresh from API first...")
            from src.services.pandascore_service import PandaScoreClient
            api_client = PandaScoreClient()
            matches = await api_client.get_upcoming_matches(limit=5)
            if matches:
                await cache_manager.cache_matches(matches, "not_started")
                upcoming_matches = await cache_manager.get_cached_matches("not_started", 10)
                print(f"   ✅ Refreshed cache, found {len(upcoming_matches)} matches")
            else:
                print("   ❌ No matches from API either")
                return
        else:
            print(f"   ✅ Found {len(upcoming_matches)} upcoming match(es)")
        
        print()
        
        # Show matches with streams
        print("2️⃣  Checking which matches have streams...")
        matches_with_streams = []
        for match in upcoming_matches:
            streams = await cache_manager.get_match_streams(match['id'])
            if streams:
                matches_with_streams.append((match, streams))
                print(f"   ✅ Match {match['id']}: {len(streams)} stream(s)")
        
        if not matches_with_streams:
            print("   ⚠️  No matches with streams found")
            print("      Let me check if we need to cache streams...")
            
            # Try to cache streams manually
            print("\n3️⃣  Caching streams from API...")
            from src.services.pandascore_service import PandaScoreClient
            api_client = PandaScoreClient()
            
            for match in upcoming_matches[:3]:
                print(f"   • Processing match {match['id']}...")
                api_match = await api_client.get_match_by_id(match['id'])
                if api_match and api_match.get('streams'):
                    await cache_manager.cache_streams(match['id'], api_match['streams'])
                    streams = await cache_manager.get_match_streams(match['id'])
                    if streams:
                        matches_with_streams.append((match, streams))
                        print(f"     ✅ Cached {len(streams)} stream(s)")
        
        if not matches_with_streams:
            print("\n   ❌ Still no matches with streams after caching")
            return
        
        print()
        
        # Augment and create embeds
        print("4️⃣  Creating Discord embeds...")
        for i, (match, streams) in enumerate(matches_with_streams[:3], 1):
            try:
                augmented = await augment_match_with_streams(
                    match, 
                    cache_manager,
                    timeout=3.0
                )
                embed = create_match_embed(augmented, status="not_started")
                
                print(f"\n   📊 Match {i}: {embed.title}")
                
                # Extract streams field from embed
                for field in embed.fields:
                    if "stream" in field.name.lower() or "transmiss" in field.name.lower():
                        print(f"      {field.name}:")
                        lines = field.value.split("\n")
                        for line in lines[:5]:  # Show first 5 lines
                            if line.strip():
                                print(f"         {line}")
                
            except Exception as e:
                print(f"   ❌ Match {i}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
        
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
    asyncio.run(test_upcoming_streams())
