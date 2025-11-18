#!/usr/bin/env python
"""
🔍 VALIDADOR DE CORRECTNESS DE TIMEZONE
========================================

Valida se as conversões de timezone estão CORRETAS matematicamente.
Compara conversões calculadas com conversões esperadas.

Uso:
    python scripts/validate_timezone_correctness.py

Exemplos de Validação:
    - UTC 15:00 → Brasil (UTC-3) = 12:00 ✓
    - UTC 15:00 → UK (UTC+0) = 15:00 ✓
    - UTC 15:00 → Japão (UTC+9) = 00:00 (next day) ✓
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.timezone_manager import TimezoneManager


class TimezoneCorrectnessValidator:
    """Validador de correctness de conversões de timezone."""
    
    def __init__(self):
        self.tm = TimezoneManager
        self.test_cases = []
        self.passed = 0
        self.failed = 0
    
    def add_test_case(
        self,
        utc_hour: int,
        utc_day: int,
        timezone: str,
        expected_hour: int,
        expected_day_offset: int = 0,
        description: str = ""
    ):
        """
        Adiciona um caso de teste.
        
        Args:
            utc_hour: Hora UTC (0-23)
            utc_day: Dia UTC (1-31)
            timezone: Timezone a testar
            expected_hour: Hora esperada no timezone
            expected_day_offset: Offset de dia esperado (0=mesmo dia, 1=próximo dia, -1=dia anterior)
            description: Descrição do teste
        """
        self.test_cases.append({
            "utc_hour": utc_hour,
            "utc_day": utc_day,
            "timezone": timezone,
            "expected_hour": expected_hour,
            "expected_day_offset": expected_day_offset,
            "description": description
        })
    
    def run_validation(self):
        """Executa todas as validações."""
        print("\n" + "="*100)
        print("🔍 VALIDADOR DE CORRECTNESS DE TIMEZONE")
        print("="*100)
        
        # Definir casos de teste padrão
        self._setup_standard_test_cases()
        
        print(f"\n📋 Executando {len(self.test_cases)} testes...\n")
        print("-" * 100)
        
        for i, test_case in enumerate(self.test_cases, 1):
            self._run_single_test(i, test_case)
        
        self._print_results_summary()
    
    def _setup_standard_test_cases(self):
        """Configura casos de teste padrão."""
        
        # Testes com UTC 15:00 (horário de partidas comuns)
        self.add_test_case(
            utc_hour=15, utc_day=20, timezone="America/Sao_Paulo",
            expected_hour=12, expected_day_offset=0,
            description="Partida 15:00 UTC em Brasil"
        )
        
        self.add_test_case(
            utc_hour=15, utc_day=20, timezone="Europe/London",
            expected_hour=15, expected_day_offset=0,
            description="Partida 15:00 UTC em Londres"
        )
        
        self.add_test_case(
            utc_hour=15, utc_day=20, timezone="Asia/Tokyo",
            expected_hour=0, expected_day_offset=1,
            description="Partida 15:00 UTC em Tóquio (próximo dia)"
        )
        
        # Teste com madrugada UTC
        self.add_test_case(
            utc_hour=3, utc_day=20, timezone="America/Sao_Paulo",
            expected_hour=0, expected_day_offset=0,
            description="Madrugada 03:00 UTC em Brasil"
        )
        
        self.add_test_case(
            utc_hour=3, utc_day=20, timezone="Asia/Tokyo",
            expected_hour=12, expected_day_offset=0,
            description="Madrugada 03:00 UTC em Tóquio"
        )
        
        # Teste com final do dia UTC
        self.add_test_case(
            utc_hour=23, utc_day=20, timezone="America/Sao_Paulo",
            expected_hour=20, expected_day_offset=0,
            description="Fim do dia 23:00 UTC em Brasil"
        )
        
        self.add_test_case(
            utc_hour=23, utc_day=20, timezone="Asia/Tokyo",
            expected_hour=8, expected_day_offset=1,
            description="Fim do dia 23:00 UTC em Tóquio (próximo dia)"
        )
        
        # Testes com outros timezones
        self.add_test_case(
            utc_hour=12, utc_day=15, timezone="America/New_York",
            expected_hour=7, expected_day_offset=0,
            description="Meio-dia UTC em New York"
        )
        
        self.add_test_case(
            utc_hour=12, utc_day=15, timezone="Australia/Sydney",
            expected_hour=23, expected_day_offset=0,
            description="Meio-dia UTC em Sydney"
        )
        
        # Teste com meia-noite UTC
        self.add_test_case(
            utc_hour=0, utc_day=15, timezone="America/Sao_Paulo",
            expected_hour=21, expected_day_offset=-1,
            description="Meia-noite 00:00 UTC em Brasil (dia anterior)"
        )
    
    def _run_single_test(self, test_num: int, test_case: dict):
        """Executa um teste individual."""
        
        utc_hour = test_case["utc_hour"]
        utc_day = test_case["utc_day"]
        timezone_name = test_case["timezone"]
        expected_hour = test_case["expected_hour"]
        expected_day_offset = test_case["expected_day_offset"]
        description = test_case["description"]
        
        # Criar datetime UTC
        dt_utc = datetime(
            year=2025,
            month=11,
            day=utc_day,
            hour=utc_hour,
            minute=0,
            tzinfo=timezone.utc
        )
        
        try:
            # Converter para timezone
            dt_local = self.tm.convert_utc_to_timezone(dt_utc, timezone_name)
            
            # Calcular esperado
            expected_day = utc_day + expected_day_offset
            
            # Validar
            hour_match = dt_local.hour == expected_hour
            day_match = dt_local.day == expected_day
            
            passed = hour_match and day_match
            
            if passed:
                self.passed += 1
                status = "✅ PASSOU"
            else:
                self.failed += 1
                status = "❌ FALHOU"
            
            # Informações da timezone
            abbr = self.tm.get_timezone_abbreviation(timezone_name)
            offset = self.tm.get_timezone_offset(timezone_name)
            emoji = self.tm.get_server_timezone_emoji(timezone_name)
            
            # Formatter saída
            print(f"\n[{test_num:2d}] {status}")
            print(f"    📝 {description}")
            print(f"    🌍 UTC: {dt_utc.strftime('%d/%m %H:%M')} → {timezone_name} ({emoji} {abbr} {offset})")
            print(f"    🕐 Esperado: {expected_day:02d}/{expected_hour:02d}:00 | Obtido: {dt_local.day:02d}/{dt_local.hour:02d}:00")
            
            if not passed:
                print(f"    ✗ ERRO: Hora={hour_match}, Dia={day_match}")
                if not hour_match:
                    print(f"      Hora esperada {expected_hour}, obtida {dt_local.hour}")
                if not day_match:
                    print(f"      Dia esperado {expected_day}, obtido {dt_local.day}")
        
        except Exception as e:
            self.failed += 1
            print(f"\n[{test_num:2d}] ❌ ERRO CRÍTICO")
            print(f"    📝 {description}")
            print(f"    🌍 {timezone_name}")
            print(f"    ✗ Exceção: {e}")
    
    def _print_results_summary(self):
        """Imprime resumo dos resultados."""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*100)
        print("📊 RESUMO")
        print("="*100)
        
        print(f"\n✅ Testes bem-sucedidos: {self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"❌ Testes falhados: {self.failed}/{total}")
        
        if pass_rate == 100:
            print("\n🎉 TODOS OS TESTES PASSARAM! A lógica de timezone está correta.")
        elif pass_rate >= 80:
            print("\n⚠️  A maioria dos testes passou. Verifique os testes falhados.")
        else:
            print("\n🚨 Muitos testes falharam. Há problemas na lógica de timezone!")
        
        print("\n" + "="*100 + "\n")


def main():
    """Função principal."""
    validator = TimezoneCorrectnessValidator()
    validator.run_validation()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Validação interrompida")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
