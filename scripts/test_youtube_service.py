#!/usr/bin/env python3
"""
Script de teste para a integração YouTube Data API v3.
Testa a extração de nomes de canais a partir de URLs do YouTube.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

from src.services.youtube_service import YouTubeService


class YouTubeServiceTester:
    """Tester para o serviço YouTube."""
    
    # URLs de teste (públicas e seguras)
    TEST_URLS = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "type": "Video (Rick Roll)",
            "expected_channel": "Rick Astley"
        },
        {
            "url": "https://youtu.be/dQw4w9WgXcQ",
            "type": "Short URL (Rick Roll)",
            "expected_channel": "Rick Astley"
        },
        {
            "url": "https://www.youtube.com/@TeamLiquid/live",
            "type": "Channel Handle (Fallback)",
            "expected_channel": "TeamLiquid"
        },
        {
            "url": "https://www.youtube.com/c/NPR",
            "type": "Custom URL (Fallback)",
            "expected_channel": "NPR"
        },
        {
            "url": "https://www.youtube.com/@elisaesports",
            "type": "Channel Handle (Fallback)",
            "expected_channel": "elisaesports"
        },
    ]
    
    def __init__(self):
        self.service = YouTubeService()
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    async def run_tests(self):
        """Executa todos os testes."""
        print("\n" + "="*80)
        print("🧪 TESTE DE INTEGRAÇÃO - YouTube Data API v3")
        print("="*80)
        
        # Verificar se API Key está configurada
        if not self.service.api_key:
            print("\n⚠️  YOUTUBE_API_KEY não configurada!")
            print("   Executando apenas testes de FALLBACK (extração de URL)")
            print("   Para testes completos, configure a chave no .env\n")
            await self.run_fallback_tests()
        else:
            print(f"\n✅ YouTube API Key configurada: {self.service.api_key[:10]}...\n")
            await self.run_full_tests()
        
        # Exibir resumo
        self.print_summary()
    
    async def run_full_tests(self):
        """Executa testes com a API."""
        for i, test_case in enumerate(self.TEST_URLS, 1):
            url = test_case["url"]
            test_type = test_case["type"]
            expected = test_case.get("expected_channel")
            
            print(f"[{i}/{len(self.TEST_URLS)}] Testando: {test_type}")
            print(f"        URL: {url}")
            
            try:
                channel_name = await self.service.get_channel_name(url)
                
                if channel_name:
                    status = "✅ PASSOU" if expected and expected.lower() in channel_name.lower() else "⚠️  PARCIAL"
                    print(f"        Canal: {channel_name}")
                    print(f"        {status}\n")
                    
                    if expected and expected.lower() in channel_name.lower():
                        self.passed += 1
                    else:
                        self.failed += 1
                else:
                    print(f"        ❌ FALHOU - Sem resposta\n")
                    self.failed += 1
                
                self.results.append({
                    "type": test_type,
                    "url": url,
                    "result": channel_name,
                    "status": "PASSOU" if channel_name else "FALHOU"
                })
                
            except Exception as e:
                print(f"        ❌ ERRO: {str(e)}\n")
                self.failed += 1
                self.results.append({
                    "type": test_type,
                    "url": url,
                    "result": f"ERRO: {str(e)}",
                    "status": "ERRO"
                })
    
    async def run_fallback_tests(self):
        """Executa testes apenas de fallback (sem API)."""
        fallback_tests = [
            {
                "url": "https://www.youtube.com/@TeamLiquid/live",
                "expected": "TeamLiquid"
            },
            {
                "url": "https://www.youtube.com/c/espn",
                "expected": "espn"
            },
            {
                "url": "https://www.youtube.com/@elisaesports",
                "expected": "elisaesports"
            },
        ]
        
        for i, test_case in enumerate(fallback_tests, 1):
            url = test_case["url"]
            expected = test_case["expected"]
            
            print(f"[{i}/{len(fallback_tests)}] Testando FALLBACK: {url}")
            
            try:
                result = await self.service._extract_channel_name_fallback(url)
                
                if result:
                    status = "✅ PASSOU" if result.lower() == expected.lower() else "⚠️  PARCIAL"
                    print(f"        Resultado: {result}")
                    print(f"        Esperado: {expected}")
                    print(f"        {status}\n")
                    
                    if result.lower() == expected.lower():
                        self.passed += 1
                    else:
                        self.failed += 1
                else:
                    print(f"        ❌ FALHOU - Sem resultado\n")
                    self.failed += 1
                
                self.results.append({
                    "type": "Fallback",
                    "url": url,
                    "result": result,
                    "status": "PASSOU" if result and result.lower() == expected.lower() else "FALHOU"
                })
                
            except Exception as e:
                print(f"        ❌ ERRO: {str(e)}\n")
                self.failed += 1
    
    def print_summary(self):
        """Exibe resumo dos testes."""
        print("="*80)
        print("📊 RESUMO DOS TESTES")
        print("="*80)
        print(f"✅ Passou:  {self.passed}")
        print(f"❌ Falhou:  {self.failed}")
        print(f"⏭️  Pulado:  {self.skipped}")
        print(f"📈 Total:   {len(self.results)}")
        
        if self.passed > 0:
            percentage = (self.passed / len(self.results)) * 100
            print(f"🎯 Taxa de sucesso: {percentage:.1f}%")
        
        print("\n" + "="*80)
        print("📋 RESULTADOS DETALHADOS")
        print("="*80)
        
        for i, result in enumerate(self.results, 1):
            status_emoji = "✅" if result["status"] == "PASSOU" else "❌" if result["status"] == "FALHOU" else "⚠️"
            print(f"\n[{i}] {status_emoji} {result['type']}")
            print(f"    URL: {result['url']}")
            print(f"    Resultado: {result['result']}")
    
    async def cleanup(self):
        """Limpa recursos."""
        await self.service.close()


async def main():
    """Função principal."""
    tester = YouTubeServiceTester()
    try:
        await tester.run_tests()
    finally:
        await tester.cleanup()
    
    print("\n✅ Testes concluídos!\n")


if __name__ == "__main__":
    asyncio.run(main())
