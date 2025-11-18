#!/usr/bin/env python3
"""
Verify that the raw_url vs embed_url bug is fixed.

Bug: When raw_url is missing, embed_url was being used as fallback.
     This caused Discord links to point to "https://player.twitch.tv/embed-error.html"
     instead of actual stream URLs.

Fix: Only use raw_url, never use embed_url for clickable links.
"""

import sys
import inspect

try:
    from src.utils.embeds import format_streams_field
    
    # Test case: Stream without raw_url (should NOT use embed_url)
    test_stream = {
        "language": "pt",
        "official": True,
        "main": True,
        "embed_url": "https://player.twitch.tv/embed-error.html?errorCode=NoParent&content=player.twitch.tv%2F%3Fchannel%3Ddust2tv",
        # raw_url is missing - this is the bug case
    }
    
    result = format_streams_field([test_stream])
    
    print("✅ TEST: Stream without raw_url")
    print(f"   Input: {test_stream}")
    print(f"   Output: {result}")
    
    # Check if it's NOT using the embed_url
    if "embed-error.html" in result:
        print("   ❌ FAIL: embed_url was used (should only use raw_url)")
        sys.exit(1)
    else:
        print("   ✅ PASS: embed_url NOT used")
    
    # Check the code for the fix
    print("\n✅ TEST: Code verification")
    code = inspect.getsource(format_streams_field)
    
    if 'stream.get("raw_url") or stream.get("embed_url"' in code:
        print("   ❌ FAIL: Still using embed_url as fallback")
        sys.exit(1)
    elif 'stream.get("raw_url", "")' in code and 'embed_url' not in code.split('for stream in streams:')[1].split('if raw_url:')[0]:
        print("   ✅ PASS: Using raw_url only (no embed_url fallback)")
    
    print("\n🟢 ALL TESTS PASSED - Bug fixed!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
