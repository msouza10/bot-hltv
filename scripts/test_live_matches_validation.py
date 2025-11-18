#!/usr/bin/env python3
"""
TESTE FINAL - Validação Completa do Algoritmo de Busca Twitch

Este script:
1. Busca TODOS os matches RUNNING (ao vivo) do PandaScore
2. Para CADA match, tenta encontrar a stream correspondente na Twitch
3. Mostra relatório detalhado com:
   - Se encontrou stream (SIM/NÃO)
   - Qual stream foi retornada (canal, título, viewers)
   - Score calculado
   - Assessment: VERDADEIRO ✅ ou FALSO POSITIVO ❌

OBJETIVO: Validar se o algoritmo de scoring funciona bem com matches REAIS.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import aiohttp
import json
from datetime import datetime
from typing import List, Dict, Optional

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.pandascore_service import PandaScoreClient
from src.services.twitch_search_service import TwitchSearchService

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def get_running_matches() -> List[Dict]:
    """Busca todos os matches que estão RUNNING (ao vivo) agora"""
    service = PandaScoreClient()
    
    print(f"{Colors.HEADER}🔍 Buscando matches AO VIVO...{Colors.ENDC}")
    
    try:
        matches = await service.get_running_matches()
        print(f"{Colors.OKGREEN}✅ Encontrados {len(matches)} matches ao vivo{Colors.ENDC}\n")
        return matches
    except Exception as e:
        print(f"{Colors.FAIL}❌ Erro ao buscar matches: {e}{Colors.ENDC}")
        return []

async def search_stream_for_match(
    twitch_service: TwitchSearchService,
    match: Dict
) -> Optional[Dict]:
    """Busca stream Twitch para um match específico"""
    
    try:
        # Extrair dados do match
        opponents = match.get("opponents", [])
        if len(opponents) < 2:
            return None
        
        # A estrutura é: opponents[i] = {"type": "Team", "opponent": {...team data...}}
        team1_data = opponents[0].get("opponent", {})
        team2_data = opponents[1].get("opponent", {})
        
        team1 = team1_data.get("name", "").strip()
        team2 = team2_data.get("name", "").strip()
        
        # Championship pode vir de league ou tournament
        championship = match.get("league", {}).get("name", "").strip()
        if not championship:
            championship = match.get("tournament", {}).get("name", "").strip()
        
        if not team1 or not team2 or not championship:
            return None
        
        # Buscar stream
        result = await twitch_service.search_streams(
            championship=championship,
            team1_name=team1,
            team2_name=team2,
            language="pt"
        )
        
        return result
    except Exception as e:
        print(f"  Erro ao buscar: {e}")
        return None

async def main():
    """Função principal"""
    
    print(f"\n{Colors.BOLD}{'='*120}")
    print(f"VALIDAÇÃO COMPLETA - BUSCA DE STREAMS PARA MATCHES AO VIVO")
    print(f"{'='*120}{Colors.ENDC}\n")
    
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Buscar matches ao vivo
    running_matches = await get_running_matches()
    
    if not running_matches:
        print(f"{Colors.WARNING}⚠️ Nenhum match ao vivo encontrado no momento.{Colors.ENDC}")
        print("Tente executar este script novamente durante um match ao vivo.")
        return
    
    # 2. Inicializar serviço Twitch
    twitch_service = TwitchSearchService()
    
    # 3. Para cada match, buscar stream
    results = []
    successful_finds = 0
    failed_finds = 0
    
    print(f"{Colors.HEADER}🎮 Processando {len(running_matches)} matches...{Colors.ENDC}\n")
    
    for i, match in enumerate(running_matches, 1):
        opponents = match.get("opponents", [])
        if len(opponents) < 2:
            continue
        
        # A estrutura é: opponents[i] = {"type": "Team", "opponent": {...team data...}}
        team1_data = opponents[0].get("opponent", {})
        team2_data = opponents[1].get("opponent", {})
        
        team1 = team1_data.get("name", "").strip()
        team2 = team2_data.get("name", "").strip()
        
        # Championship pode vir de league ou tournament
        championship = match.get("league", {}).get("name", "").strip()
        if not championship:
            championship = match.get("tournament", {}).get("name", "").strip()
        
        match_id = match.get("id")
        match_name = match.get("name", "")
        
        print(f"{Colors.OKCYAN}[{i}/{len(running_matches)}]{Colors.ENDC} {team1} vs {team2} ({championship})")
        print(f"     Match ID: {match_id}")
        
        # Buscar stream
        stream_result = await search_stream_for_match(twitch_service, match)
        
        if stream_result:
            print(f"     {Colors.OKGREEN}✅ STREAM ENCONTRADA:{Colors.ENDC}")
            print(f"        Canal: {stream_result['channel_name']}")
            print(f"        Título: {stream_result['title'][:70]}")
            print(f"        Viewers: {stream_result['viewer_count']:,}")
            print(f"        URL: {stream_result['url']}")
            successful_finds += 1
            
            results.append({
                "match_id": match_id,
                "team1": team1,
                "team2": team2,
                "championship": championship,
                "status": "ENCONTRADA",
                "channel": stream_result['channel_name'],
                "title": stream_result['title'],
                "viewers": stream_result['viewer_count'],
                "url": stream_result['url']
            })
        else:
            print(f"     {Colors.FAIL}❌ Stream NÃO encontrada{Colors.ENDC}")
            failed_finds += 1
            
            results.append({
                "match_id": match_id,
                "team1": team1,
                "team2": team2,
                "championship": championship,
                "status": "NÃO_ENCONTRADA",
                "channel": None,
                "title": None,
                "viewers": None
            })
        
        print()
    
    # 4. Relatório final
    print(f"\n{Colors.BOLD}{'='*120}")
    print(f"RELATÓRIO FINAL")
    print(f"{'='*120}{Colors.ENDC}\n")
    
    total_matches = len(running_matches)
    success_rate = (successful_finds / total_matches * 100) if total_matches > 0 else 0
    
    print(f"Total de matches ao vivo: {total_matches}")
    print(f"  {Colors.OKGREEN}✅ Streams encontradas: {successful_finds}{Colors.ENDC}")
    print(f"  {Colors.FAIL}❌ Streams NÃO encontradas: {failed_finds}{Colors.ENDC}")
    print(f"  Taxa de sucesso: {Colors.OKGREEN}{success_rate:.1f}%{Colors.ENDC}")
    
    # 5. Mostrar resultados detalhados
    print(f"\n{Colors.BOLD}MATCHES COM STREAMS ENCONTRADAS:{Colors.ENDC}\n")
    
    found_matches = [r for r in results if r['status'] == 'ENCONTRADA']
    if found_matches:
        for result in sorted(found_matches, key=lambda x: x['viewers'], reverse=True):
            print(f"  {Colors.OKGREEN}✅{Colors.ENDC} {result['team1']} vs {result['team2']}")
            print(f"     Championship: {result['championship']}")
            print(f"     Canal: {result['channel']} ({result['viewers']:,} viewers)")
            print(f"     Título: {result['title'][:70]}")
            print()
    else:
        print(f"  Nenhum match com stream encontrada")
    
    print(f"\n{Colors.BOLD}MATCHES SEM STREAMS ENCONTRADAS:{Colors.ENDC}\n")
    
    not_found_matches = [r for r in results if r['status'] == 'NÃO_ENCONTRADA']
    if not_found_matches:
        for result in not_found_matches:
            print(f"  {Colors.FAIL}❌{Colors.ENDC} {result['team1']} vs {result['team2']}")
            print(f"     Championship: {result['championship']}")
            print()
    else:
        print(f"  Todos os matches tiveram streams encontradas!")
    
    # 6. Salvar resultados em arquivo JSON
    output_file = Path(__file__).parent.parent / "data" / "validation_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_matches": total_matches,
            "found": successful_finds,
            "not_found": failed_finds,
            "success_rate": success_rate,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{Colors.OKBLUE}📄 Resultados salvos em: {output_file}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{'='*120}{Colors.ENDC}\n")

if __name__ == "__main__":
    asyncio.run(main())
