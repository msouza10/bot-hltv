#!/usr/bin/env python3
"""
Script para testar a busca automática de streams da Twitch
com matches que estão ao vivo AGORA.

Uso:
    python scripts/test_live_matches_twitch.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from pprint import pprint
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(Path(__file__).parent.parent / ".env")

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.pandascore_service import PandaScoreClient
from src.services.twitch_search_service import TwitchSearchService

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_section(text):
    """Imprime seção formatada"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*78}{Colors.ENDC}")

def print_success(text):
    """Imprime sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime warning"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    """Imprime info"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

async def fetch_running_matches():
    """Busca matches que estão rodando agora"""
    print_section("BUSCANDO MATCHES AO VIVO")
    
    try:
        client = PandaScoreClient()
        matches = await client.get_running_matches()
        
        if not matches:
            print_warning("Nenhum match ao vivo encontrado neste momento")
            return []
        
        print_success(f"Encontrados {len(matches)} matches ao vivo")
        
        for i, match in enumerate(matches, 1):
            print(f"\n{Colors.BOLD}{i}. {match.get('name', 'Desconhecido')}{Colors.ENDC}")
            print(f"   ID: {match.get('id')}")
            print(f"   Status: {match.get('status')}")
            print(f"   Início: {match.get('begin_at', 'N/A')}")
            
            opponents = match.get('opponents', [])
            if opponents:
                team1 = opponents[0].get('opponent', {}).get('name', 'Time 1')
                team2 = opponents[1].get('opponent', {}).get('name', 'Time 2') if len(opponents) > 1 else 'Time 2'
                print(f"   Match: {team1} vs {team2}")
            
            streams = match.get('streams', [])
            print(f"   Streams disponíveis: {len(streams)}")
            for stream in streams:
                raw_url = stream.get('raw_url', 'N/A')
                print(f"      • {stream.get('platform', '?')}: {raw_url[:50]}..." if len(str(raw_url)) > 50 else f"      • {stream.get('platform', '?')}: {raw_url}")
        
        return matches
        
    except Exception as e:
        print_error(f"Erro ao buscar matches: {str(e)}")
        return []

async def test_twitch_search_for_match(match):
    """Testa a busca Twitch para um match específico"""
    print_section(f"TESTANDO BUSCA TWITCH PARA: {match.get('name')}")
    
    try:
        # Extrair informações do match
        opponents = match.get('opponents', [])
        if not opponents or len(opponents) < 2:
            print_warning("Match sem informação de times completa")
            return None
        
        team1_name = opponents[0].get('opponent', {}).get('name', '')
        team2_name = opponents[1].get('opponent', {}).get('name', '')
        
        # Extrair campeonato
        league = match.get('league', {})
        championship_name = league.get('name', 'CS:GO')
        
        print_info(f"Championship: {championship_name}")
        print_info(f"Time 1: {team1_name}")
        print_info(f"Time 2: {team2_name}")
        
        # Tentar buscar stream
        print_info("Iniciando busca na Twitch...")
        
        service = TwitchSearchService()
        result = await service.search_streams(
            championship=championship_name,
            team1_name=team1_name,
            team2_name=team2_name,
            language="pt"
        )
        
        if result:
            print_success("✨ STREAM ENCONTRADO!")
            print(f"\n{Colors.BOLD}Detalhes:{Colors.ENDC}")
            print(f"  Canal: {result.get('channel_name')}")
            print(f"  URL: {result.get('url')}")
            print(f"  Viewers: {result.get('viewer_count'):,}")
            print(f"  Título: {result.get('title')}")
            print(f"  Idioma: {result.get('language', 'N/A')}")
            print(f"  Automatizado: {result.get('is_automated')}")
            
            return result
        else:
            print_warning("Nenhum stream encontrado para este match")
            return None
            
    except Exception as e:
        print_error(f"Erro ao buscar stream: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_embed_generation(match, stream=None):
    """Testa a geração do embed com o stream encontrado"""
    print_section("TESTANDO RENDERIZAÇÃO DO STREAM")
    
    try:
        # Preparar dados do match
        match_name = match.get('name', 'Match Desconhecido')
        
        print_info(f"Match: {match_name}")
        
        if stream:
            # Simular renderização
            channel = stream.get('channel_name')
            url = stream.get('url')
            viewers = stream.get('viewer_count', 0)
            language = stream.get('language', '?')
            is_automated = stream.get('is_automated', False)
            
            badge = "🤖" if is_automated else "⭐"
            
            print_success("Campo de streams renderizado:")
            print(f"\n{Colors.BOLD}Twitch{Colors.ENDC}")
            print(f"└ [{channel}]({url}) - 🇵🇹 {badge}")
            
            if is_automated:
                print(f"\n{Colors.YELLOW}🤖 Algumas streams foram encontradas automaticamente")
                print(f"   e podem não ser oficiais{Colors.ENDC}")
        else:
            print_warning("Sem stream para renderizar")
            
    except Exception as e:
        print_error(f"Erro ao gerar embed: {str(e)}")
        import traceback
        traceback.print_exc()

async def compare_with_api_streams(match, found_stream):
    """Compara o stream encontrado com os da API"""
    print_section("COMPARAÇÃO: API vs TWITCH SEARCH")
    
    api_streams = match.get('streams', [])
    
    print_info(f"Streams da API: {len(api_streams)}")
    for i, stream in enumerate(api_streams, 1):
        print(f"  {i}. {stream.get('platform', '?')}")
        print(f"     URL: {stream.get('raw_url', 'N/A')[:60]}...")
        print(f"     Viewers: {stream.get('viewer_count', 'N/A')}")
    
    if found_stream:
        print_info(f"Stream encontrado (Twitch Search):")
        print(f"  • Canal: {found_stream.get('channel_name')}")
        print(f"  • URL: {found_stream.get('url')}")
        print(f"  • Viewers: {found_stream.get('viewer_count', 0):,}")
        print_success("✨ Stream encontrado automaticamente como fallback!")
    else:
        print_warning("Nenhum stream encontrado como fallback")

async def main():
    """Função principal"""
    print_header("🔴 TESTE: BUSCA AUTOMÁTICA DE STREAMS EM MATCHES AO VIVO")
    
    print(f"{Colors.YELLOW}Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Colors.ENDC}\n")
    
    # Passo 1: Buscar matches ao vivo
    matches = await fetch_running_matches()
    
    if not matches:
        print_warning("Sem matches ao vivo para testar. Tente novamente mais tarde.")
        return
    
    # Passo 2-4: Para cada match, testar busca Twitch
    print_header("INICIANDO TESTES DE BUSCA AUTOMÁTICA")
    
    results = []
    for i, match in enumerate(matches[:3], 1):  # Testar máximo 3 matches
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'█' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}MATCH {i} de {min(3, len(matches))}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'█' * 80}{Colors.ENDC}")
        
        # Buscar stream na Twitch
        found_stream = await test_twitch_search_for_match(match)
        
        # Comparar com API
        await compare_with_api_streams(match, found_stream)
        
        # Testar geração de embed
        await test_embed_generation(match, found_stream)
        
        results.append({
            'match': match.get('name'),
            'stream_found': found_stream is not None,
            'stream': found_stream
        })
        
        # Pequeno delay para não sobrecarregar
        await asyncio.sleep(1)
    
    # Resumo final
    print_header("📊 RESUMO DOS TESTES")
    
    found_count = sum(1 for r in results if r['stream_found'])
    print_info(f"Matches testados: {len(results)}")
    print_info(f"Streams encontrados: {found_count}/{len(results)}")
    print_info(f"Taxa de sucesso: {(found_count/len(results)*100):.1f}%")
    
    if found_count > 0:
        print_success("✨ Busca automática funcionando!")
    else:
        print_warning("Nenhum stream foi encontrado neste momento")
    
    print(f"\n{Colors.BOLD}Streams encontrados:{Colors.ENDC}")
    for result in results:
        if result['stream_found']:
            print(f"  ✅ {result['match']}")
            print(f"     → {result['stream'].get('channel_name')} ({result['stream'].get('viewer_count', 0)} viewers)")
        else:
            print(f"  ❌ {result['match']}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print_error(f"Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
