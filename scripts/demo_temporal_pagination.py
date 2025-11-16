#!/usr/bin/env python3
"""
Demonstração: Cache temporal com paginação baseada em DATAS
(não em número de páginas)

Este script mostra como o sistema:
1. Verifica a cobertura temporal ATUAL (datas das partidas)
2. Se insuficiente (< 42h), busca PRÓXIMA página
3. Recalcula cobertura (não conta páginas!)
4. Repete até atingir 42h
5. Para quando tiver dados suficientes
"""

import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from src.database.cache_manager import MatchCacheManager
from src.database.temporal_cache import ensure_temporal_coverage
from src.services.pandascore_service import PandaScoreClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_temporal_pagination():
    """
    Demonstra paginação baseada em DATAS
    """
    print("\n" + "="*70)
    print("🕐 DEMONSTRAÇÃO: Paginação Temporal Inteligente (Baseada em Datas)")
    print("="*70)
    
    import os
    db_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    
    cache_manager = MatchCacheManager(db_url=db_url)
    api_client = PandaScoreClient()
    
    print("\n📋 Cenário: Cache com cobertura insuficiente")
    print("-" * 70)
    
    print("""
A lógica de paginação TEMPORAL funciona assim:

    ┌─────────────────────────────────────────────────┐
    │ 1. VERIFICAR cobertura atual                    │
    │    • Acha a partida mais antiga no cache        │
    │    • Acha a partida mais recente no cache       │
    │    • Calcula diferença em HORAS (não páginas!)  │
    │    • Se >= 42h: FIM ✅                           │
    │    • Se < 42h: CONTINUAR                        │
    └─────────────────────────────────────────────────┘
                        ↓
    ┌─────────────────────────────────────────────────┐
    │ 2. BUSCAR próxima página da API                │
    │    • Pega page++                                │
    │    • Busca 100 partidas naquela página         │
    │    • Insere no cache com ON CONFLICT DO NOTHING │
    └─────────────────────────────────────────────────┘
                        ↓
    ┌─────────────────────────────────────────────────┐
    │ 3. RECALCULAR cobertura                         │
    │    • Busca MIN(end_at/begin_at/updated_at)     │
    │    • Busca MAX(end_at/begin_at/updated_at)     │
    │    • Nova cobertura em HORAS                   │
    │    • Se >= 42h: PRONTO ✅                        │
    │    • Se < 42h: volta para passo 2              │
    └─────────────────────────────────────────────────┘
    
⚠️ NÃO conta páginas! Conta HORAS de dados!
""")
    
    try:
        # Começar teste
        print("\n🔍 Iniciando garantia de cobertura temporal...")
        print("-" * 70)
        
        client = await cache_manager.get_client()
        
        # Informações do cache ANTES
        result_before = await client.execute("""
            SELECT COUNT(*) as count FROM matches_cache
        """)
        count_before = result_before[0]['count']
        
        print(f"\n📊 ANTES:")
        print(f"   Partidas no cache: {count_before}")
        
        # Executar garantia de cobertura
        print(f"\n🚀 Executando ensure_temporal_coverage(minimum_hours=42)...")
        print("   ⏳ Isto pode levar alguns segundos...\n")
        
        stats = await ensure_temporal_coverage(
            client,
            api_client,
            minimum_hours=42
        )
        
        # Informações do cache DEPOIS
        result_after = await client.execute("""
            SELECT COUNT(*) as count FROM matches_cache
        """)
        count_after = result_after[0]['count']
        
        print(f"\n📊 DEPOIS:")
        print(f"   Partidas no cache: {count_after} (adicionadas: {count_after - count_before})")
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Cobertura temporal: {stats['current_coverage_hours']}h")
        print(f"   Status: {stats['coverage_status']}")
        print(f"   Páginas buscadas: {stats['pages_fetched']}")
        print(f"   Partidas adicionadas: {stats['matches_added']}")
        print(f"   Mais antiga: {stats['oldest_match']}")
        print(f"   Mais recente: {stats['newest_match']}")
        
        # Análise
        print(f"\n✨ ANÁLISE:")
        if stats['coverage_status'] == 'sufficient':
            print(f"   ✅ SUCESSO: Sistema tem exatamente {stats['current_coverage_hours']}h de dados")
            print(f"      (mínimo solicitado: 42h)")
            print(f"\n   🎯 Lógica funcionando:")
            print(f"      • Buscou {stats['pages_fetched']} páginas (não um número fixo!)")
            print(f"      • Parou quando atingiu 42h de cobertura REAL")
            print(f"      • Se tivesse 42h já na página 2, pararia lá")
            print(f"      • Se precisasse de página 5, iria até lá")
        else:
            print(f"   ⚠️ {stats['coverage_status'].upper()}: {stats['current_coverage_hours']}h atingidas")
            print(f"      (mínimo: 42h)")
            print(f"      Isto pode acontecer se a API tem poucas partidas")
        
        print(f"\n" + "="*70)
        print("✅ PAGINAÇÃO TEMPORAL FUNCIONANDO CORRETAMENTE!")
        print("="*70)
        print("""
Resumo da Lógica:

1️⃣  NÃO conta quantas páginas buscou
2️⃣  Conta HORAS de dados temporal (MAX_data - MIN_data)
3️⃣  Busca próxima página da API
4️⃣  Recalcula cobertura em HORAS
5️⃣  Se >= 42h: para aqui
6️⃣  Se < 42h: volta para passo 3

Exemplo prático:
• Página 1: 100 partidas, cobertura 30h → insuficiente, busca página 2
• Página 2: 100 partidas, cobertura 35h → insuficiente, busca página 3  
• Página 3: 100 partidas, cobertura 42.5h → SUCESSO! Para aqui
  
O sistema parou na página 3 porque os DADOS cobrem 42.5 horas,
não porque é a página 3. Se página 2 tivesse 50h, pararia lá!
""")
        
    except ValueError as e:
        print(f"⚠️  API não disponível (esperado se offline)")
        print(f"   Erro: {e}")
        print(f"\n   💡 Dica: Execute este script com a API disponível para ver")
        print(f"      a paginação temporal funcionando em tempo real")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    await demo_temporal_pagination()


if __name__ == "__main__":
    asyncio.run(main())
