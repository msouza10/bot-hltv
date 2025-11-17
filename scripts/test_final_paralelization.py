#!/usr/bin/env python3
"""
Teste FINAL: Simula /aovivo, /partidas e /resultados com paralelização
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cache_manager import MatchCacheManager
from src.utils.embeds import augment_match_with_streams, create_match_embed, create_result_embed


async def test_command(command_name, status, limit):
    """Testa um comando específico"""
    
    print(f"\n{'='*80}")
    print(f"🧪 TEST: Comando /{command_name}")
    print(f"{'='*80}\n")
    
    cache_mgr = MatchCacheManager()
    
    try:
        # Step 1: Buscar do cache
        print(f"1️⃣  Buscando {status} matches (max {limit})...")
        start = datetime.now()
        
        if status == "results":
            matches = await asyncio.wait_for(
                cache_mgr.get_cached_matches(status="results", hours=24, limit=limit),
                timeout=15.0
            )
        else:
            matches = await asyncio.wait_for(
                cache_mgr.get_cached_matches(status=status, limit=limit),
                timeout=15.0
            )
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ {len(matches)} matches em {elapsed:.2f}s\n")
        
        if not matches:
            print(f"   ℹ️  Nenhum match com status '{status}' no cache\n")
            return True
        
        # Step 2: Augmentar em paralelo (a fix!)
        print(f"2️⃣  Augmentando {len(matches)} matches em PARALELO...")
        start = datetime.now()
        
        augmented = await asyncio.gather(
            *[augment_match_with_streams(m, cache_mgr) for m in matches[:limit]],
            return_exceptions=True
        )
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ Augmentados em {elapsed:.2f}s\n")
        
        # Step 3: Criar embeds
        print(f"3️⃣  Criando embeds...")
        start = datetime.now()
        
        embeds = []
        for i, match in enumerate(augmented):
            try:
                if isinstance(match, Exception):
                    print(f"   ⚠️  Match {i}: Erro - {match}")
                    continue
                
                if command_name == "resultados":
                    embed = create_result_embed(match)
                else:
                    embed = create_match_embed(match)
                
                embeds.append(embed)
            except Exception as e:
                print(f"   ⚠️  Erro ao criar embed {i}: {e}")
        
        elapsed = (datetime.now() - start).total_seconds()
        print(f"   ✅ {len(embeds)} embeds criados em {elapsed:.2f}s\n")
        
        # Step 4: Verificar campos
        print(f"4️⃣  Verificando embeds:")
        has_streams = [any(f.name == "📡 Streams" for f in e.fields) for e in embeds]
        with_streams = sum(has_streams)
        print(f"   📡 {with_streams}/{len(embeds)} embeds têm streams\n")
        
        if embeds:
            print(f"5️⃣  Exemplo do primeiro embed:")
            e = embeds[0]
            print(f"   Título: {e.title}")
            print(f"   Descrição: {e.description[:60]}..." if e.description else "   Descrição: N/A")
            print(f"   Campos: {len(e.fields)}")
        
        print(f"\n{'='*80}")
        print(f"✅ {command_name.upper()} passou no teste!")
        print(f"{'='*80}\n")
        return True
        
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT! Query travando (>15s)\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n" + "="*80)
    print("🚀 TESTE COMPLETO: /partidas, /aovivo, /resultados com paralelização")
    print("="*80)
    
    results = []
    
    # Teste 1: /partidas (upcoming)
    results.append(("partidas", await test_command("partidas", "not_started", 5)))
    
    # Teste 2: /aovivo (running)
    results.append(("aovivo", await test_command("aovivo", "running", 10)))
    
    # Teste 3: /resultados (finished/canceled/postponed)
    results.append(("resultados", await test_command("resultados", "results", 5)))
    
    # Summary
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80 + "\n")
    
    all_passed = True
    for cmd, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  /{cmd:<15} {status}")
        all_passed = all_passed and passed
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
    print("="*80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
