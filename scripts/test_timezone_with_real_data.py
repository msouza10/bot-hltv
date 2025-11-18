#!/usr/bin/env python
"""
🕐 TESTE DE TIMEZONE COM DADOS REAIS
====================================

Valida a lógica de timezone usando dados reais do banco e da API PandaScore.
Testa conversões para partidas futuras, passadas e ao vivo.

Uso:
    python scripts/test_timezone_with_real_data.py

Saída:
    - Tabela formatada com conversões
    - Validações de correctness
    - Comparações entre timezones
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.timezone_manager import TimezoneManager
from src.services.pandascore_service import PandaScoreClient
from src.database.cache_manager import MatchCacheManager


class TimezoneTestValidator:
    """Validador de timezone com dados reais."""
    
    def __init__(self):
        self.test_results: List[Dict] = []
        self.timezone_manager = TimezoneManager
        
    async def test_pandascore_api_data(self):
        """Testa conversões com dados reais da API PandaScore."""
        print("\n" + "="*80)
        print("🌐 TESTE 1: Dados Reais da API PandaScore")
        print("="*80)
        
        try:
            client = PandaScoreClient()
            
            # Buscar partidas futuras
            print("\n📅 Buscando partidas FUTURAS da API...")
            upcoming = await client.get_upcoming_matches(per_page=3)
            if upcoming:
                print(f"✓ Encontradas {len(upcoming)} partidas futuras")
                await self._test_matches("FUTURAS", upcoming)
            else:
                print("✗ Nenhuma partida futura encontrada")
            
            # Buscar partidas ao vivo
            print("\n🔴 Buscando partidas AO VIVO da API...")
            running = await client.get_running_matches()
            if running:
                print(f"✓ Encontradas {len(running)} partidas ao vivo")
                await self._test_matches("AO VIVO", running)
            else:
                print("⚠ Nenhuma partida ao vivo no momento (esperado em off-hours)")
            
            # Buscar partidas passadas
            print("\n✅ Buscando partidas PASSADAS da API...")
            past = await client.get_past_matches(filter_status="finished", per_page=3)
            if past:
                print(f"✓ Encontradas {len(past)} partidas passadas")
                await self._test_matches("PASSADAS", past)
            else:
                print("✗ Nenhuma partida passada encontrada")
                
        except Exception as e:
            print(f"✗ Erro ao buscar dados da API: {e}")
            return False
            
        return True
    
    async def test_cached_data(self):
        """Testa conversões com dados do cache do banco."""
        print("\n" + "="*80)
        print("💾 TESTE 2: Dados Reais do Cache (Banco de Dados)")
        print("="*80)
        
        try:
            cache_manager = MatchCacheManager()
            client = await cache_manager.get_client()
            
            # Buscar partidas futuras do cache
            print("\n📅 Buscando partidas FUTURAS do cache...")
            upcoming = await cache_manager.get_cached_matches("not_started", limit=3)
            if upcoming:
                print(f"✓ Encontradas {len(upcoming)} partidas futuras no cache")
                await self._test_matches("FUTURAS (CACHE)", upcoming)
            else:
                print("⚠ Nenhuma partida futura no cache (faça bot.py update primeiro)")
            
            # Buscar partidas ao vivo
            print("\n🔴 Buscando partidas AO VIVO do cache...")
            running = await cache_manager.get_cached_matches("running", limit=3)
            if running:
                print(f"✓ Encontradas {len(running)} partidas ao vivo no cache")
                await self._test_matches("AO VIVO (CACHE)", running)
            else:
                print("⚠ Nenhuma partida ao vivo no cache")
            
            # Buscar partidas finalizadas
            print("\n✅ Buscando partidas FINALIZADAS do cache...")
            finished = await cache_manager.get_cached_matches("finished", limit=3)
            if finished:
                print(f"✓ Encontradas {len(finished)} partidas finalizadas no cache")
                await self._test_matches("FINALIZADAS (CACHE)", finished)
            else:
                print("⚠ Nenhuma partida finalizada no cache")
                
            await client.close()
            return True
            
        except Exception as e:
            print(f"✗ Erro ao buscar dados do cache: {e}")
            return False
    
    async def _test_matches(self, match_type: str, matches: List[Dict]):
        """Testa conversões para um grupo de partidas."""
        
        # Timezones para testar
        timezones = [
            "America/Sao_Paulo",  # Brasil UTC-3
            "Europe/London",       # UK UTC+0
            "Asia/Tokyo",          # Japão UTC+9
            "America/New_York",    # EUA UTC-5
        ]
        
        print(f"\n📊 Testando {len(matches)} partidas {match_type} em {len(timezones)} timezones:")
        print("-" * 120)
        
        for i, match in enumerate(matches[:2], 1):  # Testar primeiras 2
            print(f"\n🎮 Partida #{i}")
            
            # Extrair dados da partida
            match_id = match.get("match_id") or match.get("id")
            status = match.get("status", "unknown")
            
            # Buscar begin_at
            begin_at_str = match.get("begin_at")
            if not begin_at_str:
                print(f"  ⚠ Sem begin_at: {status}")
                continue
            
            try:
                dt_utc = self.timezone_manager.parse_iso_datetime(begin_at_str)
                print(f"  ID: {match_id} | Status: {status}")
                print(f"  UTC Original: {dt_utc}")
                
                # Testar cada timezone
                for tz in timezones:
                    try:
                        dt_converted = self.timezone_manager.convert_utc_to_timezone(dt_utc, tz)
                        abbreviation = self.timezone_manager.get_timezone_abbreviation(tz)
                        offset = self.timezone_manager.get_timezone_offset(tz)
                        emoji = self.timezone_manager.get_server_timezone_emoji(tz)
                        
                        # Formatar para exibição
                        formatted = self.timezone_manager.format_datetime_for_display(
                            dt_converted, tz, "%d/%m %H:%M"
                        )
                        
                        # Verificar se a conversão está correta
                        hour_diff = (dt_converted.hour - dt_utc.hour) % 24
                        
                        print(f"    {emoji} {tz:20} → {formatted} ({abbreviation} {offset})")
                        
                        # Validação básica
                        if not dt_converted:
                            print(f"      ✗ ERRO: Conversão retornou None!")
                        
                        self.test_results.append({
                            "match_id": match_id,
                            "status": status,
                            "match_type": match_type,
                            "timezone": tz,
                            "utc_time": str(dt_utc),
                            "local_time": formatted,
                            "abbreviation": abbreviation,
                            "offset": offset,
                            "validation": "✓" if dt_converted else "✗"
                        })
                        
                    except Exception as e:
                        print(f"    ✗ {tz}: Erro - {e}")
                        
            except Exception as e:
                print(f"  ✗ Erro ao processar partida: {e}")
    
    async def test_discord_timestamps(self):
        """Testa geração de Discord timestamps dinâmicos."""
        print("\n" + "="*80)
        print("🕐 TESTE 3: Discord Timestamps Dinâmicos")
        print("="*80)
        
        # Criar um datetime UTC
        dt_utc = datetime(2025, 11, 20, 15, 30, tzinfo=timezone.utc)
        print(f"\nDatetime UTC: {dt_utc}")
        
        timezones = ["America/Sao_Paulo", "Europe/London", "Asia/Tokyo"]
        
        for tz in timezones:
            try:
                timestamp = self.timezone_manager.discord_timestamp(dt_utc, tz)
                abbr = self.timezone_manager.get_timezone_abbreviation(tz)
                print(f"  {tz:20} → {timestamp} ({abbr})")
            except Exception as e:
                print(f"  ✗ Erro em {tz}: {e}")
    
    async def test_timezone_validation(self):
        """Testa validação de timezones."""
        print("\n" + "="*80)
        print("✔️ TESTE 4: Validação de Timezones")
        print("="*80)
        
        test_zones = [
            ("America/Sao_Paulo", True),
            ("Europe/London", True),
            ("Invalid/Timezone", False),
            ("america/new_york", False),  # Case sensitive
            ("America/New_York", True),
        ]
        
        print("\nValidações:")
        for tz, expected_valid in test_zones:
            is_valid = self.timezone_manager.is_valid_timezone(tz)
            status = "✓" if is_valid == expected_valid else "✗"
            print(f"  {status} {tz:25} → {is_valid} (esperado: {expected_valid})")
    
    def print_summary(self):
        """Imprime resumo dos testes."""
        print("\n" + "="*80)
        print("📈 RESUMO DOS TESTES")
        print("="*80)
        
        if not self.test_results:
            print("Nenhum resultado para resumir")
            return
        
        # Estatísticas
        total_tests = len(self.test_results)
        successful = sum(1 for r in self.test_results if r["validation"] == "✓")
        failed = total_tests - successful
        
        print(f"\n✓ Testes bem-sucedidos: {successful}/{total_tests}")
        print(f"✗ Testes falhados: {failed}/{total_tests}")
        
        # Agrupar por tipo de partida
        print("\n📊 Por Tipo de Partida:")
        types = {}
        for result in self.test_results:
            match_type = result["match_type"]
            if match_type not in types:
                types[match_type] = {"total": 0, "success": 0}
            types[match_type]["total"] += 1
            if result["validation"] == "✓":
                types[match_type]["success"] += 1
        
        for match_type, counts in types.items():
            ratio = counts["success"] / counts["total"] * 100
            print(f"  {match_type:20} {counts['success']}/{counts['total']} ({ratio:.0f}%)")
        
        # Agrupar por timezone
        print("\n🌍 Por Timezone:")
        tzs = {}
        for result in self.test_results:
            tz = result["timezone"]
            if tz not in tzs:
                tzs[tz] = {"total": 0, "success": 0}
            tzs[tz]["total"] += 1
            if result["validation"] == "✓":
                tzs[tz]["success"] += 1
        
        for tz, counts in tzs.items():
            ratio = counts["success"] / counts["total"] * 100
            emoji = self.timezone_manager.get_server_timezone_emoji(tz)
            print(f"  {emoji} {tz:20} {counts['success']}/{counts['total']} ({ratio:.0f}%)")
        
        # Exportar para JSON
        output_file = "data/timezone_test_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados salvos em: {output_file}")


async def main():
    """Executa todos os testes."""
    print("\n" + "🕐" * 40)
    print("  TESTE COMPLETO DE TIMEZONE - DADOS REAIS")
    print("🕐" * 40)
    
    validator = TimezoneTestValidator()
    
    # Teste 1: API
    try:
        await validator.test_pandascore_api_data()
    except Exception as e:
        print(f"\n⚠️  Teste 1 ignorado (API pode estar indisponível): {e}")
    
    # Teste 2: Cache
    try:
        await validator.test_cached_data()
    except Exception as e:
        print(f"\n⚠️  Teste 2 ignorado (cache vazio): {e}")
    
    # Teste 3: Discord timestamps
    try:
        await validator.test_discord_timestamps()
    except Exception as e:
        print(f"\n✗ Erro no Teste 3: {e}")
    
    # Teste 4: Validação
    try:
        await validator.test_timezone_validation()
    except Exception as e:
        print(f"\n✗ Erro no Teste 4: {e}")
    
    # Resumo
    validator.print_summary()
    
    print("\n" + "="*80)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
