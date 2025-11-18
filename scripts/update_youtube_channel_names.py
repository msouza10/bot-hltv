#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com nomes reais de canais do YouTube.
Útil após rodar test_youtube_real_data.py e ver que há atualizações necessárias.
"""

import asyncio
import sqlite3
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from src.services.youtube_service import YouTubeService


class YouTubeChannelUpdater:
    """Atualiza nomes de canais do YouTube no banco."""
    
    def __init__(self):
        self.service = YouTubeService()
        self.updated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def fetch_youtube_streams(self):
        """Busca todos os streams do YouTube."""
        try:
            conn = sqlite3.connect("data/bot.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT match_id, raw_url, channel_name, platform
                FROM match_streams
                WHERE platform = 'youtube'
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Erro ao buscar streams: {e}")
            return []
    
    async def update_channel_names(self):
        """Atualiza nomes de canais no banco."""
        print("\n" + "="*80)
        print("🔄 ATUALIZAÇÃO DE NOMES - YouTube Channels")
        print("="*80)
        
        if not self.service.api_key:
            print("\n⚠️  YOUTUBE_API_KEY não configurada!")
            print("   Configure a chave no .env para fazer atualizações\n")
            return
        
        # Buscar streams
        print("\n📊 Buscando streams do YouTube no banco...\n")
        streams = self.fetch_youtube_streams()
        
        if not streams:
            print("❌ Nenhum stream do YouTube encontrado")
            return
        
        print(f"✅ Encontrados {len(streams)} streams\n")
        print("="*80)
        print("🔍 PROCESSANDO ATUALIZAÇÕES")
        print("="*80 + "\n")
        
        conn = sqlite3.connect("data/bot.db")
        cursor = conn.cursor()
        
        try:
            for i, stream in enumerate(streams, 1):
                match_id = stream["match_id"]
                url = stream["raw_url"]
                current_name = stream["channel_name"]
                
                print(f"[{i}/{len(streams)}] Match {match_id}")
                print(f"          URL: {url}")
                print(f"          Nome atual: {current_name}")
                
                # Obter nome real
                real_name = await self.service.get_channel_name(url)
                
                if not real_name:
                    print(f"          ⚠️  Sem nome obtido, pulando\n")
                    self.skipped_count += 1
                    continue
                
                # Verificar se precisa atualizar
                if real_name.lower() == current_name.lower():
                    print(f"          ✅ Já atualizado: {real_name}\n")
                    self.skipped_count += 1
                    continue
                
                # Atualizar no banco
                try:
                    cursor.execute("""
                        UPDATE match_streams
                        SET channel_name = ?
                        WHERE match_id = ? AND platform = 'youtube' AND raw_url = ?
                    """, [real_name, match_id, url])
                    
                    if cursor.rowcount > 0:
                        print(f"          🎥 Atualizado para: {real_name}")
                        print(f"          ✅ {cursor.rowcount} linha(s) atualizada(s)\n")
                        self.updated_count += 1
                    else:
                        print(f"          ⚠️  Nenhuma linha foi atualizada\n")
                        self.failed_count += 1
                        
                except Exception as e:
                    print(f"          ❌ Erro ao atualizar: {e}\n")
                    self.failed_count += 1
            
            # Commit de todas as mudanças
            print("="*80)
            print("💾 SALVANDO MUDANÇAS")
            print("="*80 + "\n")
            
            conn.commit()
            print("✅ Todas as mudanças foram salvas no banco!\n")
            
        except Exception as e:
            print(f"\n❌ Erro durante atualização: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        # Resumo
        self.print_summary(len(streams))
    
    def print_summary(self, total):
        """Exibe resumo das atualizações."""
        print("="*80)
        print("📊 RESUMO DAS ATUALIZAÇÕES")
        print("="*80)
        print(f"✅ Atualizados:  {self.updated_count}")
        print(f"❌ Falhas:       {self.failed_count}")
        print(f"⏭️  Pulados:      {self.skipped_count}")
        print(f"📈 Total:        {total}")
        
        if self.updated_count > 0:
            print(f"\n🎉 {self.updated_count} canal(is) foram atualizados com sucesso!")
        else:
            print("\nℹ️  Nenhuma atualização foi necessária")
        
        print("\n" + "="*80)
    
    async def cleanup(self):
        """Limpa recursos."""
        await self.service.close()


async def main():
    """Função principal."""
    updater = YouTubeChannelUpdater()
    try:
        await updater.update_channel_names()
    finally:
        await updater.cleanup()
    
    print("\n✅ Processo concluído!\n")


if __name__ == "__main__":
    asyncio.run(main())
