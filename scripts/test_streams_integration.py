#!/usr/bin/env python3
"""
Script para testar a integração de streams com a API e cache.
Valida:
1. Extração de streams_list da API
2. Cacheamento de streams no banco
3. Recuperação de streams do cache
4. Formatação de streams para embeds
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup env
load_dotenv()

async def test_streams_integration():
    """Testa toda a pipeline de streams."""
    
    from src.services.pandascore_service import PandaScoreClient
    from src.database.cache_manager import MatchCacheManager
    from src.utils.embeds import format_streams_field, augment_match_with_streams
    
    db_url = os.getenv("LIBSQL_URL", "file:./data/bot.db")
    auth_token = os.getenv("LIBSQL_AUTH_TOKEN")
    
    logger.info("=" * 80)
    logger.info("🧪 TESTE DE INTEGRAÇÃO DE STREAMS")
    logger.info("=" * 80)
    
    # 1. Inicializar clientes
    logger.info("\n[1] Inicializando clientes...")
    try:
        api_client = PandaScoreClient()
        cache_manager = MatchCacheManager(db_url, auth_token)
        logger.info("✓ Clientes inicializados com sucesso")
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar clientes: {e}")
        return
    
    # 2. Buscar partidas da API
    logger.info("\n[2] Buscando partidas da API...")
    try:
        upcoming = await api_client.get_upcoming_matches(per_page=5)
        if not upcoming:
            logger.warning("⚠️ Nenhuma partida futura encontrada na API")
            running = await api_client.get_running_matches()
            matches = running if running else []
        else:
            matches = upcoming
        
        logger.info(f"✓ {len(matches)} partida(s) obtida(s)")
        
        if not matches:
            logger.warning("⚠️ Nenhuma partida disponível para teste")
            return
            
    except Exception as e:
        logger.error(f"✗ Erro ao buscar partidas: {e}")
        return
    
    # 3. Validar estrutura de streams
    logger.info("\n[3] Validando estrutura de streams nos dados da API...")
    test_match = matches[0]
    match_id = test_match.get("id")
    team1_name = test_match.get("opponents", [{}])[0].get("opponent", {}).get("name", "?")
    team2_name = test_match.get("opponents", [{}])[1].get("opponent", {}).get("name", "?") if len(test_match.get("opponents", [])) > 1 else "?"
    
    logger.info(f"\n   📋 Match: {team1_name} vs {team2_name} (ID: {match_id})")
    
    streams_list = test_match.get("streams_list", [])
    logger.info(f"   📡 Streams na API: {len(streams_list)}")
    
    if streams_list:
        for i, stream in enumerate(streams_list, 1):
            platform = stream.get("raw_url", "").split("/")[2].split(".")[0] if stream.get("raw_url") else "?"
            lang = stream.get("language", "?")
            official = "⭐ OFICIAL" if stream.get("official") else ""
            main = "[MAIN]" if stream.get("main") else ""
            logger.info(f"      {i}. {platform} ({lang}) {official} {main}")
            logger.info(f"         URL: {stream.get('raw_url', 'N/A')}")
    else:
        logger.warning("   ⚠️ Nenhuma stream encontrada na API")
    
    # 4. Cachear streams
    logger.info("\n[4] Cacheando streams no banco...")
    try:
        if streams_list:
            success = await cache_manager.cache_streams(match_id, streams_list)
            if success:
                logger.info(f"✓ Streams cacheadas com sucesso para match {match_id}")
            else:
                logger.warning(f"⚠️ Falha ao cachear streams")
        else:
            logger.warning("⚠️ Sem streams para cachear")
    except Exception as e:
        logger.error(f"✗ Erro ao cachear streams: {e}")
        return
    
    # 5. Recuperar streams do cache
    logger.info("\n[5] Recuperando streams do cache...")
    try:
        cached_streams = await cache_manager.get_match_streams(match_id)
        logger.info(f"✓ {len(cached_streams)} stream(s) recuperada(s) do cache")
        
        if cached_streams:
            for i, stream in enumerate(cached_streams, 1):
                logger.info(f"   {i}. {stream.get('platform')} - {stream.get('channel_name')}")
                logger.info(f"      Idioma: {stream.get('language')}")
                logger.info(f"      Oficial: {'⭐ SIM' if stream.get('is_official') else 'NÃO'}")
                logger.info(f"      Main: {'[MAIN]' if stream.get('is_main') else ''}")
    except Exception as e:
        logger.error(f"✗ Erro ao recuperar streams: {e}")
        return
    
    # 6. Testar formatação para embed
    logger.info("\n[6] Testando formatação de streams para embed...")
    try:
        if cached_streams:
            formatted = format_streams_field(cached_streams)
            if formatted:
                logger.info("✓ Streams formatadas com sucesso:\n")
                for line in formatted.split("\n"):
                    logger.info(f"   {line}")
            else:
                logger.warning("⚠️ Formatação retornou vazio")
        else:
            logger.warning("⚠️ Sem streams para formatar")
    except Exception as e:
        logger.error(f"✗ Erro ao formatar streams: {e}")
        return
    
    # 7. Testar augmentação de match com streams
    logger.info("\n[7] Testando augmentação de match com streams...")
    try:
        # Simular o que os cogs fazem
        class MockCacheManager:
            def __init__(self, real_manager):
                self.real_manager = real_manager
            
            async def get_match_streams(self, match_id):
                return await self.real_manager.get_match_streams(match_id)
        
        mock_cache = MockCacheManager(cache_manager)
        
        match_copy = test_match.copy()
        augmented = await augment_match_with_streams(match_copy, mock_cache)
        
        if "formatted_streams" in augmented:
            logger.info("✓ Match aumentado com campo 'formatted_streams'")
            logger.info("\n   Conteúdo do campo:")
            for line in augmented["formatted_streams"].split("\n"):
                logger.info(f"   {line}")
        else:
            logger.warning("⚠️ Campo 'formatted_streams' não foi adicionado")
    except Exception as e:
        logger.error(f"✗ Erro ao aumentar match: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Sucesso!
    logger.info("\n" + "=" * 80)
    logger.info("✅ TESTE CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 80)
    logger.info("\n📊 Resumo:")
    logger.info(f"   • Match testada: {team1_name} vs {team2_name}")
    logger.info(f"   • Streams na API: {len(streams_list)}")
    logger.info(f"   • Streams em cache: {len(cached_streams)}")
    logger.info(f"   • Formatação: {'✓' if formatted else '✗'}")
    logger.info(f"   • Augmentação: {'✓' if 'formatted_streams' in augmented else '✗'}")
    
    # Cleanup
    await api_client.close()
    await cache_manager.close()


if __name__ == "__main__":
    asyncio.run(test_streams_integration())
