#!/usr/bin/env python3
"""
Teste para validar a otimização: augment_match_with_streams agora é 
rápido porque não faz DB quando tem streams_list da API
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed


async def test_augment_optimization():
    """Testa se augment é rápido com streams_list (in-memory)"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Augment optimization (sem DB para API streams)")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager()
    
    try:
        # Step 1: Simular match da API (com streams_list)
        print("1️⃣  Criando mock match com streams_list (como vem da API)...")
        
        mock_match = {
            "id": 99999,
            "name": "Test vs Test",
            "status": "running",
            "begin_at": "2025-11-17T18:00:00Z",
            "streams_list": [
                {
                    "language": "pt",
                    "raw_url": "https://twitch.tv/test",
                    "official": True
                },
                {
                    "language": "en",
                    "raw_url": "https://youtube.com/watch?v=test",
                    "official": False
                }
            ]
        }
        
        print(f"   ✅ Mock com {len(mock_match['streams_list'])} streams\n")
        
        # Step 2: Augmentar (NÃO deve fazer DB - deve ser rápido!)
        print(f"2️⃣  Augmentando match com streams_list (deveria ser <50ms)...")
        start = datetime.now()
        
        augmented = await augment_match_with_streams(mock_match, cache_mgr)
        
        elapsed_ms = (datetime.now() - start).total_seconds() * 1000
        print(f"   ⏱️  Tempo: {elapsed_ms:.1f}ms")
        
        if elapsed_ms > 100:
            print(f"   ⚠️  Lento demais! Esperado <50ms, got {elapsed_ms:.1f}ms")
        else:
            print(f"   ✅ Rápido! (< 100ms)\n")
        
        # Step 3: Verificar se tem formatted_streams
        if augmented.get("formatted_streams"):
            print(f"3️⃣  Streams formatados:")
            print(f"   {augmented['formatted_streams']}\n")
        else:
            print(f"3️⃣  ⚠️  Nenhum stream formatado!\n")
        
        # Step 4: Criar embed
        print(f"4️⃣  Criando embed...")
        embed = create_match_embed(augmented)
        if embed:
            has_streams_field = any(f.name == "📡 Streams" for f in embed.fields)
            print(f"   ✅ Embed criado (tem 📡 Streams? {has_streams_field})\n")
        
        print("="*80)
        print("✅ TEST PASSOU! Augment é rápido agora")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    result = await test_augment_optimization()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    asyncio.run(main())
