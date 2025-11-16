#!/usr/bin/env python3
"""
🕐 Demonstração: Cache Temporal com Paginação Inteligente por Datas

Este script demonstra como o sistema:
1. Começa com cache vazio
2. Busca páginas 1, 2, 3... conforme necessário
3. Continua até ter 42 horas de cobertura
4. Para automaticamente quando atinge o objetivo
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict

sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from src.services.pandascore_service import PandaScoreClient
from src.database.temporal_cache import TemporalCacheManager


async def demo_intelligent_pagination():
    """Demonstra paginação inteligente baseada em datas"""
    
    print("\n" + "="*70)
    print("🕐 DEMONSTRAÇÃO: PAGINAÇÃO INTELIGENTE POR DATAS (42h)")
    print("="*70)
    
    try:
        api_client = PandaScoreClient()
    except ValueError:
        print("⚠️ API key não configurada - usando simulação")
        api_client = None
    
    # Simular cache em construção
    all_matches = []
    page = 1
    min_hours = 42
    
    print(f"\n📋 Meta: Coletar {min_hours} horas de cobertura temporal")
    print("   Strategy: Paginar através de partidas finalizadas até atingir objetivo\n")
    
    # Simular window temporal
    start_window, end_window = TemporalCacheManager.get_temporal_window()
    print(f"🕐 Janela temporal alvo:")
    print(f"   Início: {start_window.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   Fim:    {end_window.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   Duração: {min_hours}h\n")
    
    while True:
        print(f"📄 Buscando página {page} de partidas finalizadas...")
        
        try:
            # Buscar página (ou simular se API indisponível)
            if api_client:
                page_matches = await api_client.get_past_matches(per_page=100, page=page)
            else:
                # Simulação: gerar 80-100 matches fictícios por página
                print("   (Usando simulação de dados)")
                num_matches = 95 - (page - 1) * 15  # Menos matches em páginas posteriores
                if num_matches <= 0:
                    page_matches = []
                else:
                    # Gerar matches com datas realistas
                    now = datetime.now(timezone.utc)
                    page_matches = []
                    for i in range(num_matches):
                        match_index = (page - 1) * 100 + i
                        days_ago = (match_index * 0.3)  # ~0.3 dias por match
                        match = {
                            "id": 1000000 + match_index,
                            "end_at": (now - timedelta(days=days_ago)).isoformat(),
                            "begin_at": (now - timedelta(days=days_ago, hours=1)).isoformat(),
                            "status": "finished"
                        }
                        page_matches.append(match)
            
            if not page_matches:
                print(f"   ✗ API retornou vazio (fim dos dados)\n")
                break
            
            print(f"   ✅ Encontradas {len(page_matches)} partidas")
            
            # Analisar datas nesta página
            page_dates = []
            for match in page_matches:
                all_matches.append(match)
                
                # Extrair data de referência
                anchor = TemporalCacheManager.get_match_temporal_anchor(match)
                if anchor:
                    page_dates.append(anchor)
            
            if page_dates:
                oldest_page = min(page_dates)
                newest_page = max(page_dates)
                print(f"      Datas nesta página:")
                print(f"        • Mais antiga: {oldest_page.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                print(f"        • Mais recente: {newest_page.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Calcular cobertura total até agora
            if all_matches:
                all_dates = []
                for m in all_matches:
                    anchor = TemporalCacheManager.get_match_temporal_anchor(m)
                    if anchor:
                        all_dates.append(anchor)
                
                if all_dates:
                    coverage_start = min(all_dates)
                    coverage_end = max(all_dates)
                    coverage_hours = (coverage_end - coverage_start).total_seconds() / 3600
                    
                    print(f"\n   📊 Cobertura cumulativa:")
                    print(f"      Total de partidas coletadas: {len(all_matches)}")
                    print(f"      Período coberto: {coverage_hours:.1f} horas")
                    print(f"      De: {coverage_start.strftime('%Y-%m-%d %H:%M')} UTC")
                    print(f"      Até: {coverage_end.strftime('%Y-%m-%d %H:%M')} UTC")
                    
                    # Verificar se atingiu objetivo
                    if coverage_hours >= min_hours:
                        print(f"\n   ✅ OBJETIVO ATINGIDO! {coverage_hours:.1f}h >= {min_hours}h")
                        print(f"   🛑 Parando paginação (requisito atendido)\n")
                        break
                    else:
                        remaining = min_hours - coverage_hours
                        print(f"      Faltam: {remaining:.1f}h para {min_hours}h")
                        print(f"      → Continuando para página {page+1}...\n")
            
            page += 1
            
            # Proteção contra paginação infinita
            if page > 20:
                print(f"\n⚠️ Limite de páginas (20) atingido. Parando.")
                break
            
        except Exception as e:
            print(f"   ✗ Erro ao buscar página: {e}")
            break
    
    # Resumo final
    print("="*70)
    print("📊 RESUMO FINAL")
    print("="*70)
    print(f"Total de páginas consultadas: {page - 1}")
    print(f"Total de partidas coletadas: {len(all_matches)}")
    
    if all_matches:
        all_dates = []
        for m in all_matches:
            anchor = TemporalCacheManager.get_match_temporal_anchor(m)
            if anchor:
                all_dates.append(anchor)
        
        if all_dates:
            coverage_start = min(all_dates)
            coverage_end = max(all_dates)
            coverage_hours = (coverage_end - coverage_start).total_seconds() / 3600
            
            print(f"Cobertura temporal: {coverage_hours:.1f} horas")
            print(f"Período: {coverage_start.strftime('%Y-%m-%d %H:%M')} até {coverage_end.strftime('%Y-%m-%d %H:%M')} UTC")
            print(f"Status: {'✅ ADEQUADO' if coverage_hours >= min_hours else '⚠️ INSUFICIENTE'}")
    
    print("="*70)
    print("\n💡 Como funciona:")
    print("   1. Começa sem cache (página 1)")
    print("   2. Busca primeira página (até 100 partidas)")
    print("   3. Calcula período coberto pelas partidas")
    print("   4. Se < 42h: vai para próxima página")
    print("   5. Repete até ter 42 horas ou atingir limite")
    print("   6. Armazena TODAS no banco com ON CONFLICT DO NOTHING")
    print("   7. Próximo update: limpeza remove partidas > 42h antigas")
    print("\n✨ Resultado: Cache sempre com 42h de dados frescos!\n")


async def demo_cleanup_flow():
    """Demonstra como a limpeza funciona após armazenar"""
    
    print("="*70)
    print("🧹 DEMONSTRAÇÃO: FLUXO DE LIMPEZA TEMPORAL")
    print("="*70)
    
    print("\n📝 Cenário: Após paginação, temos 200 partidas com 50h de cobertura")
    print("\nFluxo de execução (a cada 15 minutos):\n")
    
    demo_flow = [
        ("1. Fetch upcoming (pag 1)", "50 partidas", "🟦 Próximas"),
        ("2. Fetch running", "5 partidas", "🔴 Ao vivo"),
        ("3. Fetch finished (pag 1-3)", "150 partidas", "🟩 Finalizadas"),
        ("4. Cache all", "205 partidas", "💾 Banco de dados"),
        ("", "", ""),
        ("5. CLEANUP_EXPIRED", "-54 partidas", "🗑️ Remove > 42h"),
        ("   Resultado", "151 partidas", "✅ Exatamente 42h"),
        ("", "", ""),
        ("6. COVERAGE_CHECK", "Cobertura: 42.1h", "📊 Verifica suficiência"),
        ("   Status", "ADEQUATE", "✅ OK, não precisa mais páginas"),
    ]
    
    for step, action, detail in demo_flow:
        if not step:
            print()
        else:
            print(f"{step:<25} {action:<20} {detail}")
    
    print("\n" + "="*70)
    print("\n🎯 Resultado do fluxo:")
    print("   ✅ Cache sempre com 42 horas de dados")
    print("   ✅ Sem dados antigos acumulando")
    print("   ✅ Sem paginação desnecessária")
    print("   ✅ Performance consistente\n")


async def demo_edge_cases():
    """Demonstra casos extremos"""
    
    print("="*70)
    print("⚠️ DEMONSTRAÇÃO: CASOS EXTREMOS")
    print("="*70)
    
    cases = [
        {
            "titulo": "Caso 1: Gap na API (fim de semana, poucos matches)",
            "descricao": "Se não há matches suficientes para 42h, o que acontece?",
            "resultado": [
                "• Paginação continua até página 20 (limite)",
                "• Coleta ALL matches disponíveis",
                "• Se < 42h: status = 'PARTIAL_COVERAGE'",
                "• Sistema continua funcionando com cobertura reduzida"
            ]
        },
        {
            "titulo": "Caso 2: Muitos matches (temporada intensa)",
            "descricao": "Se há mais de 300 matches em 42h?",
            "resultado": [
                "• Página 1: 100 matches",
                "• Página 2: 100 matches",
                "• Página 3: 100 matches",
                "• PARA! Já tem 42h (provavelmente em página 2)",
                "• Ignora página 3+ (não precisa)"
            ]
        },
        {
            "titulo": "Caso 3: Primeira execução (cache vazio)",
            "descricao": "Sistema recém ligado, sem dados?",
            "resultado": [
                "• Coverage check detecta cache vazio",
                "• Começa com página 1, vai até 42h",
                "• Pode pegar páginas 1-5 ou mais",
                "• Populate cache inicial em ~1-2 segundos",
                "• Próximo update: mantém cobertura"
            ]
        },
    ]
    
    for i, case in enumerate(cases, 1):
        print(f"\n{case['titulo']}")
        print(f"{'─' * 70}")
        print(f"📝 {case['descricao']}")
        print(f"\n✅ Resultado:")
        for resultado in case['resultado']:
            print(f"   {resultado}")
    
    print("\n" + "="*70 + "\n")


async def main():
    try:
        await demo_intelligent_pagination()
        await demo_cleanup_flow()
        await demo_edge_cases()
        
        print("✨ DEMONSTRAÇÃO COMPLETA!")
        print("\n📚 Referência:")
        print("   • Implementação: src/database/temporal_cache.py")
        print("   • Integração: src/services/cache_scheduler.py")
        print("   • Testes: scripts/test_temporal_cache.py")
        print("   • Docs: docs/TEMPORAL_CACHE_DESIGN.md\n")
        
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
