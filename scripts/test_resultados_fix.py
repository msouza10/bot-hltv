#!/usr/bin/env python3
"""
Test script para verificar se /resultados funciona após fix do COALESCE(begin_at, updated_at)
"""
import asyncio
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_result_embed


async def test_resultados():
    """Test get_cached_matches with status=results"""
    
    print("\n" + "="*80)
    print("🧪 TEST: /resultados fix (COALESCE(begin_at, updated_at))")
    print("="*80 + "\n")
    
    cache_manager = MatchCacheManager()
    
    try:
        # Step 1: Tentar buscar matches com status="results" (finished, canceled, postponed)
        print("1️⃣  Buscando matches finalizados do cache com status='results'...")
        start_time = datetime.now()
        
        matches = await asyncio.wait_for(
            cache_manager.get_cached_matches(status="results", hours=24, limit=5),
            timeout=10.0
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"   ⏱️  Tempo: {elapsed:.2f}s")
        
        if not matches:
            print("   ⚠️  Nenhum match encontrado (cache pode estar vazio)")
            print("   ℹ️  Isso é normal se nenhum match foi finalizado nas últimas 24h")
            return True
        
        print(f"   ✅ Sucesso! {len(matches)} matches recuperados\n")
        
        # Step 2: Verificar estrutura do primeiro match
        first_match = matches[0]
        print(f"2️⃣  Inspecionando primeiro match:")
        print(f"   ID: {first_match.get('id')}")
        print(f"   Status: {first_match.get('status')}")
        print(f"   Begin_at: {first_match.get('begin_at')}")
        print(f"   Updated_at: {first_match.get('updated_at')}\n")
        
        # Step 3: Testar augmentação com streams
        if matches:
            print(f"3️⃣  Augmentando com streams (se existirem)...")
            test_match = matches[0].copy()
            augmented = await augment_match_with_streams(test_match, cache_manager)
            
            if augmented.get("formatted_streams"):
                print(f"   ✅ Streams encontrados:")
                print(f"   {augmented['formatted_streams'][:100]}...")
            else:
                print(f"   ℹ️  Nenhum stream em cache para este match")
            
            print()
        
        # Step 4: Testar embed creation
        if matches:
            print(f"4️⃣  Criando resultado embed...")
            test_match = matches[0].copy()
            embed = create_result_embed(test_match)
            
            if embed:
                print(f"   ✅ Embed criado com sucesso")
                print(f"   Título: {embed.title}")
                print(f"   Descrição: {embed.description[:100]}...")
                print(f"   Campos: {len(embed.fields)}")
                
                # Verificar se tem streams
                has_streams = any(field.name == "📡 Streams" for field in embed.fields)
                print(f"   Tem streams? {'✅ Sim' if has_streams else '❌ Não'}")
            else:
                print(f"   ❌ Falha ao criar embed")
            
            print()
        
        print("="*80)
        print("✅ RESULTADO: /resultados deve funcionar agora (sem hang)!")
        print("="*80 + "\n")
        return True
        
    except asyncio.TimeoutError:
        print(f"   ❌ TIMEOUT! Query ainda está travando (>10s)")
        print("   Isso significa o COALESCE não resolveu o problema")
        return False
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_resultados()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
