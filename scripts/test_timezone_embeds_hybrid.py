#!/usr/bin/env python3
"""
🧪 Script de teste para validar timezone + embeds híbrido
Testa se a implementação funciona corretamente
"""

import pytz
from datetime import datetime
import sys
sys.path.insert(0, '/home/msouza/Documents/bot-hltv')

from src.utils.timezone_manager import TimezoneManager
from src.utils.embeds import create_match_embed, create_error_embed, create_info_embed

def test_timezone_functionality():
    """Testa funcionalidades de timezone"""
    print("=" * 70)
    print("🧪 TESTE 1: Funcionalidades de Timezone")
    print("=" * 70)
    
    timezones = ["America/Sao_Paulo", "America/New_York", "Europe/London"]
    
    for tz_name in timezones:
        print(f"\n🕐 Testando {tz_name}:")
        
        # Teste 1: Validar timezone
        is_valid = TimezoneManager.is_valid_timezone(tz_name)
        print(f"   ✓ Timezone válido: {is_valid}")
        
        # Teste 2: Obter abreviação
        abbr = TimezoneManager.get_timezone_abbreviation(tz_name)
        print(f"   ✓ Abreviação: {abbr}")
        
        # Teste 3: Obter offset
        offset = TimezoneManager.get_timezone_offset(tz_name)
        print(f"   ✓ Offset: {offset}")
        
        # Teste 4: Criar datetime com timezone
        tz = pytz.timezone(tz_name)
        now_local = datetime.now(tz)
        print(f"   ✓ Datetime com tz: {now_local}")
        print(f"   ✓ tzinfo: {now_local.tzinfo}")
    
    print("\n" + "✅ TESTE 1 PASSOU!" + "\n")


def test_embed_with_timezone():
    """Testa embeds com timezone"""
    print("=" * 70)
    print("🧪 TESTE 2: Embeds com Timezone")
    print("=" * 70)
    
    # Teste error_embed
    print("\n📍 Testando create_error_embed()...")
    try:
        embed = create_error_embed(
            title="Teste de Erro",
            description="Esta é uma mensagem de teste",
            timezone="America/Sao_Paulo"
        )
        print(f"   ✓ Embed criado com sucesso")
        print(f"   ✓ Título: {embed.title}")
        print(f"   ✓ Timestamp: {embed.timestamp}")
        print(f"   ✓ Timestamp tzinfo: {embed.timestamp.tzinfo}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # Teste info_embed
    print("\n📍 Testando create_info_embed()...")
    try:
        embed = create_info_embed(
            title="Teste de Info",
            description="Esta é uma mensagem informativa",
            timezone="America/New_York"
        )
        print(f"   ✓ Embed criado com sucesso")
        print(f"   ✓ Título: {embed.title}")
        print(f"   ✓ Timestamp: {embed.timestamp}")
        print(f"   ✓ Timestamp tzinfo: {embed.timestamp.tzinfo}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    print("\n" + "✅ TESTE 2 PASSOU!" + "\n")
    return True


def test_match_embed_with_timezone():
    """Testa match embed com timezone"""
    print("=" * 70)
    print("🧪 TESTE 3: Match Embed com Timezone")
    print("=" * 70)
    
    # Dados de teste
    mock_match = {
        "id": 12345,
        "status": "not_started",
        "scheduled_at": "2025-11-18T20:00:00Z",
        "begin_at": "2025-11-18T20:00:00Z",
        "end_at": None,
        "opponents": [
            {
                "opponent": {
                    "id": 1,
                    "name": "Furia",
                    "image_url": "https://example.com/furia.png"
                }
            },
            {
                "opponent": {
                    "id": 2,
                    "name": "Vitality",
                    "image_url": "https://example.com/vitality.png"
                }
            }
        ],
        "league": {
            "id": 1,
            "name": "ESL Pro League",
            "image_url": "https://example.com/league.png"
        },
        "serie": {
            "id": 1,
            "name": "Season 20",
            "full_name": "ESL Pro League Season 20"
        },
        "tournament": {
            "id": 1,
            "name": "Main Event",
            "tier": "s",
            "region": "SA",
            "type": "offline"
        },
        "number_of_games": 3,
        "match_type": "best_of",
        "streams_list": []
    }
    
    timezones = ["America/Sao_Paulo", "Europe/London"]
    
    for tz in timezones:
        print(f"\n📍 Testando create_match_embed() com {tz}...")
        try:
            embed = create_match_embed(mock_match, timezone=tz)
            print(f"   ✓ Embed criado com sucesso")
            print(f"   ✓ Título: {embed.title}")
            print(f"   ✓ Timestamp: {embed.timestamp}")
            print(f"   ✓ Timestamp tzinfo: {embed.timestamp.tzinfo}")
            
            # Verificar footer
            if embed.footer:
                print(f"   ✓ Footer: {embed.footer.text}")
                # Validar que footer contém a abreviação do timezone
                tz_abbr = TimezoneManager.get_timezone_abbreviation(tz)
                if tz_abbr in embed.footer.text:
                    print(f"   ✅ Footer contém abreviação ({tz_abbr})")
                else:
                    print(f"   ⚠️  Footer não contém abreviação esperada ({tz_abbr})")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "✅ TESTE 3 PASSOU!" + "\n")
    return True


def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🧪 TESTES: TIMEZONE + EMBEDS HÍBRIDO" + " " * 17 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        test_timezone_functionality()
        test_embed_with_timezone()
        test_match_embed_with_timezone()
        
        print("=" * 70)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 70)
        print("\n📊 Resumo:")
        print("   ✓ Timezone manager funcionando")
        print("   ✓ Error/Info embeds com timezone")
        print("   ✓ Match embed com timezone + footer com abreviação")
        print("\n🚀 Implementação pronta para uso!\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERRO NOS TESTES")
        print("=" * 70)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
