#!/usr/bin/env python
"""
⚡ TESTE DE PERFORMANCE DE TIMEZONE
===================================

Avalia a performance das conversões de timezone.
Importante para garantir que conversões não impactam a latência do bot.

Uso:
    python scripts/benchmark_timezone_performance.py

Métricas:
    - Tempo por conversão
    - Throughput (conversões/segundo)
    - Tempo de parsing ISO
    - Tempo de formatação para exibição
"""

import sys
import os
import time
from datetime import datetime, timezone
from typing import Tuple, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.timezone_manager import TimezoneManager


class TimezonePerformanceBenchmark:
    """Benchmark de performance de timezone."""
    
    def __init__(self):
        self.tm = TimezoneManager
        self.results: List[dict] = []
    
    def benchmark_parse_iso(self, iterations: int = 10000) -> Tuple[float, float]:
        """Faz benchmark de parsing ISO."""
        iso_string = "2025-11-20T15:30:45Z"
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.tm.parse_iso_datetime(iso_string)
        end = time.perf_counter()
        
        total_time = (end - start) * 1000  # em ms
        avg_time = total_time / iterations
        
        return total_time, avg_time
    
    def benchmark_convert_utc(self, iterations: int = 10000) -> Tuple[float, float]:
        """Faz benchmark de conversão UTC → timezone."""
        dt_utc = datetime(2025, 11, 20, 15, 30, tzinfo=timezone.utc)
        timezone_name = "America/Sao_Paulo"
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.tm.convert_utc_to_timezone(dt_utc, timezone_name)
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        avg_time = total_time / iterations
        
        return total_time, avg_time
    
    def benchmark_format_display(self, iterations: int = 10000) -> Tuple[float, float]:
        """Faz benchmark de formatação para exibição."""
        dt_utc = datetime(2025, 11, 20, 15, 30, tzinfo=timezone.utc)
        dt_local = self.tm.convert_utc_to_timezone(dt_utc, "America/Sao_Paulo")
        timezone_name = "America/Sao_Paulo"
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.tm.format_datetime_for_display(dt_local, timezone_name, "%d/%m/%Y %H:%M")
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        avg_time = total_time / iterations
        
        return total_time, avg_time
    
    def benchmark_discord_timestamp(self, iterations: int = 10000) -> Tuple[float, float]:
        """Faz benchmark de Discord timestamp."""
        dt_utc = datetime(2025, 11, 20, 15, 30, tzinfo=timezone.utc)
        timezone_name = "America/Sao_Paulo"
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.tm.discord_timestamp(dt_utc, timezone_name)
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        avg_time = total_time / iterations
        
        return total_time, avg_time
    
    def benchmark_validate_timezone(self, iterations: int = 10000) -> Tuple[float, float]:
        """Faz benchmark de validação de timezone."""
        timezone_name = "America/Sao_Paulo"
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.tm.is_valid_timezone(timezone_name)
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        avg_time = total_time / iterations
        
        return total_time, avg_time
    
    def benchmark_multiple_timezones(self, num_conversions: int = 5000) -> dict:
        """Faz benchmark de conversão para múltiplos timezones."""
        dt_utc = datetime(2025, 11, 20, 15, 30, tzinfo=timezone.utc)
        timezones = [
            "America/Sao_Paulo",
            "Europe/London",
            "Asia/Tokyo",
            "America/New_York",
            "Australia/Sydney",
        ]
        
        start = time.perf_counter()
        for _ in range(num_conversions):
            for tz in timezones:
                self.tm.convert_utc_to_timezone(dt_utc, tz)
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        total_conversions = num_conversions * len(timezones)
        avg_per_conversion = total_time / total_conversions
        throughput = total_conversions / ((end - start))  # por segundo
        
        return {
            "total_time_ms": total_time,
            "total_conversions": total_conversions,
            "avg_per_conversion_ms": avg_per_conversion,
            "throughput_per_second": throughput
        }
    
    def benchmark_full_pipeline(self, num_iterations: int = 1000) -> dict:
        """Faz benchmark do pipeline completo (parse + convert + format)."""
        iso_string = "2025-11-20T15:30:45Z"
        timezone_name = "America/Sao_Paulo"
        
        start = time.perf_counter()
        for _ in range(num_iterations):
            dt_utc = self.tm.parse_iso_datetime(iso_string)
            dt_local = self.tm.convert_utc_to_timezone(dt_utc, timezone_name)
            formatted = self.tm.format_datetime_for_display(dt_local, timezone_name, "%d/%m/%Y %H:%M")
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        avg_per_iteration = total_time / num_iterations
        
        return {
            "total_time_ms": total_time,
            "iterations": num_iterations,
            "avg_per_iteration_ms": avg_per_iteration,
            "throughput_per_second": num_iterations / ((end - start))
        }
    
    def run_all_benchmarks(self):
        """Executa todos os benchmarks."""
        print("\n" + "⚡" * 40)
        print("  BENCHMARK DE PERFORMANCE DE TIMEZONE")
        print("⚡" * 40)
        
        print("\n" + "="*80)
        print("⏱️  TESTES INDIVIDUAIS (10.000 iterações cada)")
        print("="*80)
        
        # Teste 1: Parse ISO
        print("\n1️⃣  Parse ISO DateTime:")
        total, avg = self.benchmark_parse_iso()
        print(f"   Total:   {total:.2f} ms")
        print(f"   Média:   {avg:.4f} ms por operação")
        print(f"   Throughput: {10000/total*1000:.0f} ops/seg")
        self.results.append({"operation": "parse_iso", "avg_ms": avg, "throughput": 10000/total*1000})
        
        # Teste 2: Convert UTC
        print("\n2️⃣  Conversão UTC → Timezone Local:")
        total, avg = self.benchmark_convert_utc()
        print(f"   Total:   {total:.2f} ms")
        print(f"   Média:   {avg:.4f} ms por operação")
        print(f"   Throughput: {10000/total*1000:.0f} ops/seg")
        self.results.append({"operation": "convert_utc", "avg_ms": avg, "throughput": 10000/total*1000})
        
        # Teste 3: Format Display
        print("\n3️⃣  Formatação para Exibição:")
        total, avg = self.benchmark_format_display()
        print(f"   Total:   {total:.2f} ms")
        print(f"   Média:   {avg:.4f} ms por operação")
        print(f"   Throughput: {10000/total*1000:.0f} ops/seg")
        self.results.append({"operation": "format_display", "avg_ms": avg, "throughput": 10000/total*1000})
        
        # Teste 4: Discord Timestamp
        print("\n4️⃣  Discord Timestamp:")
        total, avg = self.benchmark_discord_timestamp()
        print(f"   Total:   {total:.2f} ms")
        print(f"   Média:   {avg:.4f} ms por operação")
        print(f"   Throughput: {10000/total*1000:.0f} ops/seg")
        self.results.append({"operation": "discord_timestamp", "avg_ms": avg, "throughput": 10000/total*1000})
        
        # Teste 5: Validate Timezone
        print("\n5️⃣  Validação de Timezone:")
        total, avg = self.benchmark_validate_timezone()
        print(f"   Total:   {total:.2f} ms")
        print(f"   Média:   {avg:.4f} ms por operação")
        print(f"   Throughput: {10000/total*1000:.0f} ops/seg")
        self.results.append({"operation": "validate_tz", "avg_ms": avg, "throughput": 10000/total*1000})
        
        # Teste 6: Múltiplos timezones
        print("\n" + "="*80)
        print("🌍 TESTE MULTI-TIMEZONE (5 timezones, 5.000 iterações)")
        print("="*80)
        
        result = self.benchmark_multiple_timezones(5000)
        print(f"\n6️⃣  Conversões Múltiplas:")
        print(f"   Total:   {result['total_time_ms']:.2f} ms")
        print(f"   Conversões: {result['total_conversions']}")
        print(f"   Média:   {result['avg_per_conversion_ms']:.4f} ms por conversão")
        print(f"   Throughput: {result['throughput_per_second']:.0f} conversões/seg")
        self.results.append({"operation": "multi_tz", "avg_ms": result['avg_per_conversion_ms'], "throughput": result['throughput_per_second']})
        
        # Teste 7: Pipeline completo
        print("\n" + "="*80)
        print("🔄 PIPELINE COMPLETO (Parse + Convert + Format, 1.000 iterações)")
        print("="*80)
        
        result = self.benchmark_full_pipeline(1000)
        print(f"\n7️⃣  Pipeline Completo:")
        print(f"   Total:   {result['total_time_ms']:.2f} ms")
        print(f"   Iterações: {result['iterations']}")
        print(f"   Média:   {result['avg_per_iteration_ms']:.4f} ms por ciclo")
        print(f"   Throughput: {result['throughput_per_second']:.0f} ciclos/seg")
        self.results.append({"operation": "full_pipeline", "avg_ms": result['avg_per_iteration_ms'], "throughput": result['throughput_per_second']})
        
        self._print_performance_summary()
    
    def _print_performance_summary(self):
        """Imprime resumo de performance."""
        print("\n" + "="*80)
        print("📊 RESUMO DE PERFORMANCE")
        print("="*80)
        
        print("\nOperação                         Tempo Médio    Throughput")
        print("-" * 70)
        
        for result in self.results:
            op = result["operation"]
            avg = result["avg_ms"]
            throughput = result["throughput"]
            
            # Formatar nome
            if op == "parse_iso":
                display_name = "Parse ISO DateTime"
            elif op == "convert_utc":
                display_name = "Conversão UTC → Timezone"
            elif op == "format_display":
                display_name = "Formatação para Exibição"
            elif op == "discord_timestamp":
                display_name = "Discord Timestamp"
            elif op == "validate_tz":
                display_name = "Validação de Timezone"
            elif op == "multi_tz":
                display_name = "Conversão (5 timezones)"
            elif op == "full_pipeline":
                display_name = "Pipeline Completo"
            else:
                display_name = op
            
            print(f"  {display_name:28} {avg:8.4f} ms  {throughput:10.0f} ops/s")
        
        # Análise
        print("\n" + "-"*70)
        print("🔍 Análise:")
        
        slowest = max(self.results, key=lambda x: x['avg_ms'])
        fastest = min(self.results, key=lambda x: x['avg_ms'])
        
        print(f"\n  ✓ Operação mais rápida: {fastest['operation']} ({fastest['avg_ms']:.4f} ms)")
        print(f"  ⚠ Operação mais lenta: {slowest['operation']} ({slowest['avg_ms']:.4f} ms)")
        
        # Validar latência
        print("\n✔️  Validação de Latência:")
        avg_pipeline = next(r['avg_ms'] for r in self.results if r['operation'] == 'full_pipeline')
        
        if avg_pipeline < 1.0:
            print(f"  ✅ Pipeline {avg_pipeline:.4f} ms - EXCELENTE (< 1ms)")
        elif avg_pipeline < 5.0:
            print(f"  ✅ Pipeline {avg_pipeline:.4f} ms - BOM (< 5ms)")
        elif avg_pipeline < 10.0:
            print(f"  ⚠️  Pipeline {avg_pipeline:.4f} ms - ACEITÁVEL (< 10ms)")
        else:
            print(f"  ❌ Pipeline {avg_pipeline:.4f} ms - LENTO (> 10ms)")
        
        print("\n" + "="*80 + "\n")


def main():
    """Função principal."""
    benchmark = TimezonePerformanceBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrompido")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
