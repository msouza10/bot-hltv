#!/usr/bin/env python
"""
⏰ CONVERSOR INTERATIVO DE TIMEZONE
===================================

Permite testar conversões de timezone de forma interativa.
Útil para validar conversões manualmente durante desenvolvimento.

Uso:
    python scripts/interactive_timezone_converter.py

Exemplos de Entrada:
    15:00 UTC
    12:30 America/Sao_Paulo
    23:45 Europe/London to Asia/Tokyo
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.timezone_manager import TimezoneManager


class InteractiveTimezoneConverter:
    """Conversor interativo de timezone."""
    
    def __init__(self):
        self.tm = TimezoneManager
        self.common_timezones = {
            "1": "America/Sao_Paulo",
            "2": "America/New_York",
            "3": "Europe/London",
            "4": "Europe/Paris",
            "5": "Asia/Tokyo",
            "6": "Australia/Sydney",
            "7": "Asia/Dubai",
            "8": "Asia/Shanghai",
        }
    
    def show_menu(self):
        """Mostra menu principal."""
        print("\n" + "="*80)
        print("⏰ CONVERSOR INTERATIVO DE TIMEZONE")
        print("="*80)
        print("\n📋 Opções:")
        print("  1. Converter hora UTC para um timezone")
        print("  2. Converter hora para múltiplos timezones")
        print("  3. Listar timezones comuns")
        print("  4. Validar timezone")
        print("  5. Ver offsets de todos timezones comuns")
        print("  6. Sair")
        print("\n" + "-"*80)
        return input("Escolha uma opção (1-6): ").strip()
    
    def option_1_convert_single(self):
        """Converte hora UTC para um timezone."""
        print("\n" + "="*80)
        print("🔄 CONVERTER UTC PARA UM TIMEZONE")
        print("="*80)
        
        # Pedir hora
        time_str = input("\n⏰ Digite a hora em formato HH:MM (ex: 15:30): ").strip()
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                raise ValueError("Formato inválido")
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError("Hora ou minuto inválido")
        except:
            print("✗ Hora inválida!")
            return
        
        # Pedir timezone
        tz = input("🌍 Digite o timezone de destino (ex: America/Sao_Paulo): ").strip()
        
        if not self.tm.is_valid_timezone(tz):
            print(f"✗ Timezone inválido: {tz}")
            return
        
        # Criar datetime UTC
        dt_utc = datetime(2025, 11, 20, hour, minute, tzinfo=timezone.utc)
        
        # Converter
        try:
            dt_local = self.tm.convert_utc_to_timezone(dt_utc, tz)
            abbr = self.tm.get_timezone_abbreviation(tz)
            offset = self.tm.get_timezone_offset(tz)
            emoji = self.tm.get_server_timezone_emoji(tz)
            
            print(f"\n✅ Resultado:")
            print(f"  UTC:      {dt_utc.strftime('%H:%M')}")
            print(f"  {tz} {emoji}")
            print(f"  Local:    {dt_local.strftime('%H:%M')}")
            print(f"  Offset:   {offset}")
            print(f"  Sigla:    {abbr}")
            
            # Discord timestamp
            timestamp = self.tm.discord_timestamp(dt_utc, tz)
            print(f"  Discord:  {timestamp}")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def option_2_convert_multiple(self):
        """Converte hora para múltiplos timezones."""
        print("\n" + "="*80)
        print("🔄 CONVERTER PARA MÚLTIPLOS TIMEZONES")
        print("="*80)
        
        # Pedir hora
        time_str = input("\n⏰ Digite a hora em formato HH:MM (ex: 15:30): ").strip()
        try:
            parts = time_str.split(":")
            hour, minute = int(parts[0]), int(parts[1])
        except:
            print("✗ Hora inválida!")
            return
        
        # Pedir timezones
        print("\n🌍 Digite os timezones (um por linha, vazio para terminar):")
        timezones = []
        while True:
            tz = input(f"  Timezone {len(timezones)+1}: ").strip()
            if not tz:
                break
            if not self.tm.is_valid_timezone(tz):
                print(f"    ✗ Timezone inválido: {tz}, tente novamente")
                continue
            timezones.append(tz)
        
        if not timezones:
            print("✗ Nenhum timezone fornecido!")
            return
        
        # Criar datetime UTC
        dt_utc = datetime(2025, 11, 20, hour, minute, tzinfo=timezone.utc)
        
        # Converter
        print(f"\n✅ Resultado (UTC {dt_utc.strftime('%H:%M')}):\n")
        print("-" * 60)
        
        for tz in timezones:
            try:
                dt_local = self.tm.convert_utc_to_timezone(dt_utc, tz)
                abbr = self.tm.get_timezone_abbreviation(tz)
                offset = self.tm.get_timezone_offset(tz)
                emoji = self.tm.get_server_timezone_emoji(tz)
                
                print(f"  {emoji} {tz:25} → {dt_local.strftime('%H:%M')} ({abbr} {offset})")
            except Exception as e:
                print(f"  ✗ {tz:25} → Erro: {e}")
        
        print("-" * 60)
    
    def option_3_list_common(self):
        """Lista timezones comuns."""
        print("\n" + "="*80)
        print("📋 TIMEZONES COMUNS")
        print("="*80)
        
        print("\n  Código | Timezone")
        print("  " + "-"*50)
        
        for code, tz in self.common_timezones.items():
            abbr = self.tm.get_timezone_abbreviation(tz)
            offset = self.tm.get_timezone_offset(tz)
            emoji = self.tm.get_server_timezone_emoji(tz)
            
            print(f"    {code}   | {emoji} {tz:25} ({abbr} {offset})")
    
    def option_4_validate_timezone(self):
        """Valida um timezone."""
        print("\n" + "="*80)
        print("✔️  VALIDAR TIMEZONE")
        print("="*80)
        
        tz = input("\n🌍 Digite o timezone: ").strip()
        
        if self.tm.is_valid_timezone(tz):
            abbr = self.tm.get_timezone_abbreviation(tz)
            offset = self.tm.get_timezone_offset(tz)
            emoji = self.tm.get_server_timezone_emoji(tz)
            
            print(f"\n✅ Timezone válido!")
            print(f"  Nome:     {tz}")
            print(f"  Emoji:    {emoji}")
            print(f"  Sigla:    {abbr}")
            print(f"  Offset:   {offset}")
        else:
            print(f"\n✗ Timezone inválido: {tz}")
            
            # Sugerir similares
            suggestions = self._find_similar_timezones(tz)
            if suggestions:
                print(f"\n  Sugestões:")
                for suggestion in suggestions[:5]:
                    print(f"    • {suggestion}")
    
    def option_5_show_offsets(self):
        """Mostra offsets de timezones comuns."""
        print("\n" + "="*80)
        print("📊 OFFSETS DE TIMEZONES COMUNS")
        print("="*80)
        
        print("\nTimezone                          Offset  Sigla  Emoji")
        print("-" * 65)
        
        for code, tz in self.common_timezones.items():
            abbr = self.tm.get_timezone_abbreviation(tz)
            offset = self.tm.get_timezone_offset(tz)
            emoji = self.tm.get_server_timezone_emoji(tz)
            
            print(f"  {tz:30} {offset:>6}  {abbr:>4}  {emoji}")
    
    def _find_similar_timezones(self, search_term: str, limit: int = 5):
        """Encontra timezones similares."""
        import pytz
        
        search_lower = search_term.lower()
        similar = []
        
        for tz in pytz.all_timezones:
            if search_lower in tz.lower():
                similar.append(tz)
        
        return similar[:limit]
    
    def run(self):
        """Executa o conversor interativo."""
        print("\n" + "🕐" * 40)
        print("\n  CONVERSOR INTERATIVO DE TIMEZONE")
        print("  Testador de Lógica de Conversão\n")
        print("🕐" * 40)
        
        while True:
            option = self.show_menu()
            
            if option == "1":
                self.option_1_convert_single()
            elif option == "2":
                self.option_2_convert_multiple()
            elif option == "3":
                self.option_3_list_common()
            elif option == "4":
                self.option_4_validate_timezone()
            elif option == "5":
                self.option_5_show_offsets()
            elif option == "6":
                print("\n👋 Até logo!\n")
                break
            else:
                print("✗ Opção inválida!")


def main():
    """Função principal."""
    converter = InteractiveTimezoneConverter()
    converter.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Conversor interrompido")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
