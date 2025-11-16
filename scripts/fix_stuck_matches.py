#!/usr/bin/env python3
"""
Script para limpar partidas travadas (running há muito tempo)
Verifica se mudaram para finished e atualiza o cache
"""
import asyncio
import sys
sys.path.insert(0, '/root/workspace')

from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager

async def fix_stuck_matches():
    """Detecta e corrige partidas travadas"""
    api = PandaScoreClient()
    cache = MatchCacheManager()
    
    print("=" * 80)
    print("🔧 LIMPANDO PARTIDAS TRAVADAS")
    print("=" * 80)
    
    # IDs das partidas que estão travadas
    stuck_ids = [1267674, 1257801]
    
    for match_id in stuck_ids:
        print(f"\n🔍 Verificando partida ID: {match_id}")
        print("-" * 80)
        
        try:
            # Buscar partida em finished
            finished = await api.get_past_matches(per_page=100)
            
            found = False
            for match in finished:
                if match.get('id') == match_id:
                    print(f"✅ ENCONTRADA em FINISHED!")
                    print(f"   Nome: {match.get('name')}")
                    print(f"   Status: {match.get('status')}")
                    print(f"   Resultado: {match.get('results', [])}")
                    print(f"   End_at: {match.get('end_at')}")
                    
                    # Atualizar no cache
                    print(f"\n   📊 Atualizando cache...")
                    stats = await cache.cache_matches([match], "stuck_fix")
                    print(f"   ✅ Cache atualizado: {stats['updated']} partidas atualizadas")
                    found = True
                    break
            
            if not found:
                print(f"❌ Partida NÃO encontrada em FINISHED")
                print(f"   Tentando em RUNNING...")
                
                # Tentar em running
                running = await api.get_running_matches()
                for match in running:
                    if match.get('id') == match_id:
                        print(f"⚠️  Partida AINDA está em RUNNING")
                        print(f"   Nome: {match.get('name')}")
                        print(f"   Status: {match.get('status')}")
                        found = True
                        break
                
                if not found:
                    print(f"❓ Partida não encontrada em nenhum status")
                    print(f"   (Pode ter sido cancelada ou removida da API)")
        
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    await api.close()
    await cache.close()
    
    print("\n" + "=" * 80)
    print("✅ PROCESSO CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(fix_stuck_matches())
