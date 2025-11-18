#!/usr/bin/env python3
"""
Script de teste para YouTube Service usando URLs reais das partidas ao vivo.
Extrai URLs do banco de dados e testa a extração de nomes de canais.
"""

import asyncio
import os
import sys
import sqlite3
from dotenv import load_dotenv

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

from src.services.youtube_service import YouTubeService


class YouTubeRealDataTester:
    """Tester usando dados reais do banco de dados."""
    
    def __init__(self):
        self.service = YouTubeService()
        self.results = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
    
    def fetch_youtube_streams_from_db(self):
        """Busca URLs reais de YouTube do banco de dados."""
        try:
            conn = sqlite3.connect("data/bot.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar streams do YouTube
            cursor.execute("""
                SELECT DISTINCT match_id, raw_url, channel_name, language, is_official
                FROM match_streams
                WHERE platform = 'youtube'
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados do banco: {e}")
            return []
    
    async def run_tests(self):
        """Executa testes com dados reais."""
        print("\n" + "="*80)
        print("🧪 TESTE COM DADOS REAIS - YouTube Streams das Partidas")
        print("="*80)
        
        # Verificar API Key
        if not self.service.api_key:
            print("\n⚠️  YOUTUBE_API_KEY não configurada!")
            print("   Configure a chave no .env para testes completos\n")
        else:
            print(f"\n✅ YouTube API Key configurada\n")
        
        # Buscar dados do banco
        print("📊 Buscando URLs de YouTube do banco de dados...\n")
        youtube_streams = self.fetch_youtube_streams_from_db()
        
        if not youtube_streams:
            print("❌ Nenhum stream do YouTube encontrado no banco de dados")
            print("   Execute o bot para popular o banco primeiro:\n")
            print("   venv/bin/python -m src.bot\n")
            return
        
        print(f"✅ Encontrados {len(youtube_streams)} streams do YouTube\n")
        print("="*80)
        print("🔍 TESTANDO EXTRAÇÃO DE NOMES")
        print("="*80 + "\n")
        
        # Testar cada stream
        for i, stream in enumerate(youtube_streams, 1):
            match_id = stream.get("match_id")
            url = stream.get("raw_url")
            current_channel = stream.get("channel_name")
            language = stream.get("language")
            is_official = stream.get("is_official")
            
            print(f"[{i}/{len(youtube_streams)}] Match ID: {match_id}")
            print(f"           URL: {url}")
            print(f"           Canal atual no DB: {current_channel}")
            print(f"           Idioma: {language} | Oficial: {bool(is_official)}")
            
            try:
                # Tentar extrair nome real
                real_channel_name = await self.service.get_channel_name(url)
                
                if real_channel_name:
                    # Verificar se é diferente do que está no DB
                    if real_channel_name.lower() != current_channel.lower():
                        print(f"           🎥 Nome real obtido: {real_channel_name}")
                        print(f"           ✅ DIFERENTE - Deveria ser atualizado\n")
                        self.passed += 1
                    else:
                        print(f"           ✅ Nome correto: {real_channel_name}\n")
                        self.passed += 1
                else:
                    print(f"           ⚠️  Sem nome obtido (usando fallback)\n")
                    self.failed += 1
                
                self.results.append({
                    "match_id": match_id,
                    "url": url,
                    "current": current_channel,
                    "obtained": real_channel_name,
                    "status": "OK" if real_channel_name else "FALHOU"
                })
                
            except Exception as e:
                print(f"           ❌ ERRO: {str(e)}\n")
                self.errors += 1
                self.results.append({
                    "match_id": match_id,
                    "url": url,
                    "current": current_channel,
                    "obtained": f"ERRO: {str(e)}",
                    "status": "ERRO"
                })
        
        # Resumo
        self.print_summary(youtube_streams)
    
    def print_summary(self, total_streams):
        """Exibe resumo dos testes."""
        print("="*80)
        print("📊 RESUMO DOS TESTES")
        print("="*80)
        print(f"✅ Sucessos:  {self.passed}")
        print(f"❌ Falhas:    {self.failed}")
        print(f"⚠️  Erros:    {self.errors}")
        print(f"📈 Total:     {len(self.results)}")
        
        if len(self.results) > 0:
            percentage = (self.passed / len(self.results)) * 100
            print(f"🎯 Taxa de sucesso: {percentage:.1f}%")
        
        # Mostrar URLs que precisam atualização
        needs_update = [r for r in self.results if r["obtained"] and r["obtained"] != r["current"]]
        if needs_update:
            print(f"\n🔄 URLs que deveriam ser atualizadas: {len(needs_update)}")
            for result in needs_update:
                print(f"\n   Match {result['match_id']}:")
                print(f"   Atual:  {result['current']}")
                print(f"   Novo:   {result['obtained']}")
        
        print("\n" + "="*80)
        print("📋 RESULTADOS DETALHADOS")
        print("="*80)
        
        for i, result in enumerate(self.results, 1):
            status_emoji = "✅" if result["status"] == "OK" else "❌"
            print(f"\n[{i}] {status_emoji} Match {result['match_id']}")
            print(f"    URL: {result['url']}")
            print(f"    Canal no DB: {result['current']}")
            print(f"    Obtido: {result['obtained']}")
    
    async def cleanup(self):
        """Limpa recursos."""
        await self.service.close()


async def main():
    """Função principal."""
    tester = YouTubeRealDataTester()
    try:
        await tester.run_tests()
    finally:
        await tester.cleanup()
    
    print("\n✅ Testes concluídos!\n")


if __name__ == "__main__":
    asyncio.run(main())
