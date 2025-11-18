# Copilot Instructions Update Summary

**Date**: November 18, 2025
**File Updated**: `.github/copilot-instructions.md`

## Overview

The copilot instructions have been comprehensively updated to reflect the current state of the bot-hltv codebase, incorporating all major features and architectural decisions that evolved since the last documentation update.

## Key Updates Made

### 1. Architecture Section - Enhanced

- **Before**: Generic 3-tier cache flow diagram
- **After**: Detailed 9-stage data flow showing stream integration pipeline

Stream integration now explicitly documented:
- PandaScore API → streams_list extraction
- Temporal cache (42h window) management
- Stream persistence in `match_streams` table
- Parallel augmentation with `augment_match_with_streams()`
- Embed creation with 📡 Streams field

### 2. Core Components - Expanded

Added documentation for:
- **temporal_cache.py** - 42-hour sliding window management
- **twitch_search_service.py** - Optional stream enrichment (OAuth2, 1h token cache)
- **youtube_service.py** - Optional stream enrichment (URL parsing)

Clarified dual-cache implementation in cache_manager:
- `cache_streams()` method for stream persistence
- `get_match_streams()` method for retrieval

### 3. Database Schema - Updated

Now documents:
- **match_streams table** ✨ NEW with platform, channel_name, language, official/main flags
- Indexing strategy for performance
- 7 tables total (was 6) + foreign keys
- Indexed lookups for fast stream retrieval

### 4. Integration Points - New Sections Added

#### Twitch & YouTube Services
- TwitchSearchService: Fallback search when `streams_list` is sparse. Uses OAuth2 client credentials flow. Token cached 1h.
- YouTubeService: Extracts channel info from YouTube URLs. Supports video IDs, channel handles, and live URLs. Optional (YOUTUBE_API_KEY in .env).
- **Key insight**: Both services are optional enrichment - primary stream data comes from PandaScore `streams_list`

#### Temporal Cache (42-hour window)
- Purpose: Keep cache relevant without manual cleanup. Uses `begin_at` field for temporal ordering.
- Implementation: `temporal_cache.py` maintains sliding window. Queries filter by `begin_at >= now - 42h` and `begin_at <= now + some_buffer`
- Used by: Cache scheduler to decide which matches to keep, avoiding stale data
- Pattern: Call `ensure_temporal_coverage()` before rendering match lists

### 5. Key Files Reference Table - Comprehensive

Added 5 new entries:
- `src/services/twitch_search_service.py`
- `src/services/youtube_service.py`
- `src/database/temporal_cache.py`
- Updated cache_manager.py functions: `cache_streams()`, `get_match_streams()`
- New embed functions: `augment_match_with_streams()`, `format_streams_field()`

### 6. Project Status - Updated

- **From**: "MVP with 24h/1h/live/result notifications"
- **To**: "Production-ready with 42h temporal cache, multi-stream support, and result notifications"
- Stack now includes: "Twitch/YouTube APIs"

## What Required No Changes

These sections were already accurate and current:

- ✅ Running the Bot (workflow still valid)
- ✅ Database Setup instructions
- ✅ Developer Workflows (cog/feature/scheduler patterns unchanged)
- ✅ Async Patterns & Conventions (3-tier cache, timeout enforcement)
- ✅ Logging conventions (UTF-8, emoji prefixes)
- ✅ Error handling patterns
- ✅ Notification deduplication logic
- ✅ PandaScore API response variations (comprehensive edge cases)
- ✅ Common pitfalls & solutions
- ✅ Directory organization (production files in src/, scripts/, docs/)

## Critical Patterns Now Documented

### Stream Integration Pipeline
```python
# Standard pattern in all cogs
match = await augment_match_with_streams(match, self.bot.cache_manager)
embed = create_match_embed(match)  # Now includes 📡 Streams field
```

### Cache Hierarchy
1. Memory cache (get_cached_matches_fast) - <100ms
2. libSQL DB (get_cached_matches) - <3s
3. API fallback - expensive, avoid in hot paths

### Stream Formatting
- Grouped by platform (Twitch, Kick, YouTube, Facebook)
- Language flags (🇧🇷, 🇬🇧, 🇷🇺, etc.)
- Official marker (⭐)
- Main stream marker ([MAIN])

## File Structure & Conventions

All documented patterns remain valid:

- `/src/` - Production code (bot.py, cogs/, services/, database/, utils/)
- `/scripts/` - Development & testing scripts (check_*, analyze_*, test_*, fix_*)
- `/docs/` - Documentation (ARQUITETURA_*, GUIA_*, MELHORIAS_*, etc.)
- `/plan/` - Project planning (TODO.md, ROADMAP.md, etc.)

## Environment Variables

All documented variables are current and optional ones added:

- DISCORD_TOKEN (required)
- PANDASCORE_API_KEY (required)
- TESTING_GUILD_ID (recommended)
- LIBSQL_URL
- LIBSQL_AUTH_TOKEN (optional)
- **NEW** TWITCH_CLIENT_ID (optional, for fallback stream search)
- **NEW** TWITCH_CLIENT_SECRET (optional, for fallback stream search)
- **NEW** YOUTUBE_API_KEY (optional, for YouTube stream enrichment)

## Testing & Validation Scripts

All documented scripts are still valid:

- `scripts/check_*.py` - API/cache verification
- `scripts/test_*.py` - Feature tests (including new `test_streams_integration.py`)
- `scripts/analyze_*.py` - Data analysis
- `scripts/monitor_reminders_realtime.py` - Real-time debugging

## Recommendations for AI Agents Using These Instructions

**To be immediately productive with this codebase:**

1. **Understand data flow first**: Read the architecture diagram (now 9 stages)
2. **Know the cache hierarchy**: Memory → DB → API (never reverse this order)
3. **Always augment matches**: Call `augment_match_with_streams()` before creating embeds
4. **Respect the 3s timeout**: Wrap DB calls in try/except, use memory cache first
5. **Handle stream data**: Use `format_streams_field()` to display streams properly
6. **Check temporal window**: Keep matches within 42h using `ensure_temporal_coverage()`
7. **Reference key files**: Use the Key Files Reference table for function locations
8. **Debug with scripts**: Use check_*.py and monitor_*.py for real-time inspection

---

**Update Status**: ✅ Complete  
**File Size**: 439 lines  
**Verification Date**: November 18, 2025  
**Codebase Alignment**: Latest with stream integration v1 + temporal cache 42h
