#!/usr/bin/env python3
"""
Script para testar busca de stream em TEMPO REAL para um match ao vivo AGORA.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
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

async def main():
    """Função principal"""
    print_header("🔴 TESTE EM TEMPO REAL: Busca de Stream para Match Ao Vivo")
    
    print(f"{Colors.YELLOW}Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Colors.ENDC}\n")
    
    # Passo 1: Buscar um match ao vivo
    print_section("BUSCANDO UM MATCH AO VIVO AGORA")
    
    try:
        client = PandaScoreClient()
        matches = await client.get_running_matches()
        
        if not matches:
            print_warning("Nenhum match ao vivo encontrado neste momento")
            return
        
        print_success(f"Encontrados {len(matches)} matches ao vivo")
        
        # Pegar o primeiro match
        match = matches[0]
        
        print(f"\n{Colors.BOLD}Match selecionado:{Colors.ENDC}")
        print(f"  Nome: {match.get('name')}")
        print(f"  ID: {match.get('id')}")
        print(f"  Status: {match.get('status')}")
        
        # Extrair informações
        opponents = match.get('opponents', [])
        if len(opponents) < 2:
            print_warning("Match sem informação de times completa")
            return
        
        team1_name = opponents[0].get('opponent', {}).get('name', '')
        team2_name = opponents[1].get('opponent', {}).get('name', '')
        
        league = match.get('league', {})
        championship_name = league.get('name', 'Unknown')
        
        print(f"  Championship: {championship_name}")
        print(f"  Team 1: {team1_name}")
        print(f"  Team 2: {team2_name}")
        
        # Passo 2: Buscar na Twitch
        print_section("BUSCANDO STREAM NA TWITCH")
        
        print_info(f"Procurando stream para:")
        print_info(f"  Campeonato: {championship_name}")
        print_info(f"  Time 1: {team1_name}")
        print_info(f"  Time 2: {team2_name}")
        
        service = TwitchSearchService()
        result = await service.search_streams(
            championship=championship_name,
            team1_name=team1_name,
            team2_name=team2_name,
            language="pt"
        )
        
        print_section("RESULTADO")
        
        if result:
            print_success("🎉 STREAM ENCONTRADA!")
            print(f"\n{Colors.BOLD}Detalhes:{Colors.ENDC}")
            print(f"  Canal: {result.get('channel_name')}")
            print(f"  URL: {result.get('url')}")
            print(f"  Viewers: {result.get('viewer_count'):,}")
            print(f"  Título: {result.get('title')}")
            print(f"  Idioma: {result.get('language', 'N/A')}")
            print(f"  Automatizado: {result.get('is_automated')}")
            
            print(f"\n{Colors.GREEN}✨ A stream foi encontrada automaticamente!{Colors.ENDC}")
            
        else:
            print_warning("Nenhuma stream encontrada com palavras-chave")
            print_info("Isso significa:")
            print_info("  - Não havia streams com campeonato/times no título")
            print_info("  - OU a stream não atingiu score mínimo (15 pts)")
            
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print_error(f"Erro fatal: {str(e)}")
        sys.exit(1)
