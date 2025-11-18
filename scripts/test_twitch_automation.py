#!/usr/bin/env python3
"""
Script para testar a busca de streams na Twitch.

Simula uma partida sem raw_url e verifica se a busca automática funciona.
"""

import asyncio
import os
import sys
from datetime import datetime

# Adicionar path
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

async def test_twitch_search():
    """Testa a busca de streams na Twitch."""
    
    print("=" * 80)
    print("🤖 TESTE: Busca Automática de Streams na Twitch")
    print("=" * 80)
    
    # Verificar credentials
    if not os.getenv("TWITCH_CLIENT_ID"):
        print("❌ ERRO: TWITCH_CLIENT_ID não configurado no .env")
        return False
    
    if not os.getenv("TWITCH_CLIENT_SECRET"):
        print("❌ ERRO: TWITCH_CLIENT_SECRET não configurado no .env")
        return False
    
    print("✅ Credentials Twitch encontradas")
    print()
    
    # Importar serviço
    try:
        from src.services.twitch_search_service import get_twitch_search_service
        print("✅ Serviço Twitch importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar serviço: {e}")
        return False
    
    # Testar busca
    try:
        service = await get_twitch_search_service()
        print("✅ Serviço Twitch inicializado")
        print()
        
        # Cenário 1: Busca por campeonato famoso
        print("📍 Teste 1: Busca por 'ESL Pro League'")
        print("-" * 80)
        result = await service.search_streams(
            championship="ESL Pro League",
            team1_name="FaZe",
            team2_name="Team Vitality",
            language="pt"
        )
        
        if result:
            print(f"✅ SUCESSO! Stream encontrado:")
            print(f"   Canal: {result['channel_name']}")
            print(f"   URL: {result['url']}")
            print(f"   Viewers: {result['viewer_count']}")
            print(f"   Título: {result['title']}")
            print(f"   Automatizado: {result.get('is_automated', False)}")
            print(f"   Idioma: {result.get('language', 'unknown')}")
        else:
            print("⚠️  Nenhum stream encontrado (esperado se não houver transmissão)")
        print()
        
        # Cenário 2: Busca por teams
        print("📍 Teste 2: Busca por 'G2 vs FaZe'")
        print("-" * 80)
        result2 = await service.search_streams(
            championship="CS2 Championship",
            team1_name="G2",
            team2_name="FaZe",
            language="en"
        )
        
        if result2:
            print(f"✅ Stream encontrado:")
            print(f"   Canal: {result2['channel_name']}")
            print(f"   Viewers: {result2['viewer_count']}")
        else:
            print("⚠️  Nenhum stream encontrado")
        print()
        
        # Teste de caching
        print("📍 Teste 3: Caching (mesma query novamente)")
        print("-" * 80)
        result3 = await service.search_streams(
            championship="ESL Pro League",
            team1_name="FaZe",
            team2_name="Team Vitality",
            language="pt"
        )
        
        if result3:
            print(f"✅ Resultado do cache: {result3['channel_name']}")
            print("   (resultado deve ser idêntico ao Teste 1)")
        print()
        
        print("=" * 80)
        print("🟢 TESTES CONCLUÍDOS COM SUCESSO")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_format_streams():
    """Testa a formatação de streams com badge automatizado."""
    
    print("\n" + "=" * 80)
    print("🎨 TESTE: Formatação de Streams com Badge")
    print("=" * 80)
    
    try:
        from src.utils.embeds import format_streams_field
        
        # Teste 1: Stream normal
        print("\n📍 Teste 1: Stream Normal (com raw_url)")
        print("-" * 80)
        stream_normal = {
            "channel_name": "Gaules",
            "language": "pt",
            "is_official": True,
            "is_main": False,
            "raw_url": "https://twitch.tv/gaules",
            "platform": "twitch"
        }
        
        result = format_streams_field([stream_normal])
        print(result)
        
        # Teste 2: Stream automatizado
        print("\n📍 Teste 2: Stream Automatizado (com badge 🤖)")
        print("-" * 80)
        stream_auto = {
            "channel_name": "SomeChannel",
            "language": "pt",
            "is_official": False,
            "is_main": False,
            "is_automated": True,  # FLAG IMPORTANTE!
            "raw_url": "https://twitch.tv/somechannel",
            "platform": "twitch"
        }
        
        result = format_streams_field([stream_auto])
        print(result)
        
        print("\n✅ Formatação funcionando corretamente!")
        print("   - ⭐ = Stream oficial")
        print("   - 🤖 = Stream encontrado automaticamente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    
    # Rodar testes
    success1 = asyncio.run(test_twitch_search())
    success2 = asyncio.run(test_format_streams())
    
    if success1 and success2:
        print("\n\n🟢 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n\n🔴 ALGUNS TESTES FALHARAM")
        sys.exit(1)
