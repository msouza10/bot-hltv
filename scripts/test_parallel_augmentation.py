#!/usr/bin/env python3
"""
Test para verificar se a paralelização com asyncio.gather() resolveu o hang
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed


async def test_parallel_augmentation():
    """Testa augmentação paralela de múltiplos matches"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Paralelização com asyncio.gather()")
    print("="*80 + "\n")
    
    cache_mgr = MatchCacheManager()
    
    try:
        # Step 1: Buscar matches ao vivo
        print("1️⃣  Buscando matches em running (simulando /aovivo)...")
        start = datetime.now()
        
        matches = await asyncio.wait_for(
            cache_mgr.get_cached_matches(status="running", limit=10),
            timeout=15.0
        )
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ {len(matches)} matches encontrados em {elapsed:.2f}s\n")
        
        if not matches:
            print("   ℹ️  Nenhum match em running no cache")
            return True
        
        # Step 2: Augmentar em paralelo (o jeito novo)
        print(f"2️⃣  Augmentando {len(matches)} matches em PARALELO com asyncio.gather()...")
        start = datetime.now()
        
        augmented = await asyncio.gather(
            *[augment_match_with_streams(m, cache_mgr) for m in matches],
            return_exceptions=True
        )
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ Augmentados em {elapsed:.2f}s\n")
        
        # Step 3: Contar quantos tiveram sucesso
        success_count = sum(1 for m in augmented if not isinstance(m, Exception))
        error_count = sum(1 for m in augmented if isinstance(m, Exception))
        
        print(f"3️⃣  Resultados:")
        print(f"   ✅ {success_count} matches augmentados com sucesso")
        if error_count > 0:
            print(f"   ⚠️  {error_count} matches falharam")
            for i, m in enumerate(augmented):
                if isinstance(m, Exception):
                    print(f"      - Match {i}: {m}")
        
        # Step 4: Verificar streams
        print(f"\n4️⃣  Verificando streams:")
        matches_with_streams = sum(1 for m in augmented if not isinstance(m, Exception) and m.get("formatted_streams"))
        print(f"   📡 {matches_with_streams} matches com streams")
        
        # Step 5: Testar criação de embeds
        print(f"\n5️⃣  Criando embeds em paralelo...")
        start = datetime.now()
        
        embeds_results = []
        for match in augmented:
            try:
                if isinstance(match, Exception):
                    continue
                embed = create_match_embed(match)
                embeds_results.append(embed)
            except Exception as e:
                logger.error(f"Erro: {e}")
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ {len(embeds_results)} embeds criados em {elapsed:.2f}s\n")
        
        print("="*80)
        print("✅ TESTE PASSOU! Paralelização está funcionando.")
        print("="*80 + "\n")
        return True
        
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT! Ainda está travando\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_parallel_augmentation())
    sys.exit(0 if result else 1)
