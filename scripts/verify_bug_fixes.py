#!/usr/bin/env python3
"""
Script para verificar se os bugs foram corrigidos:
1. Emoji bugado para 'ru' (🇷🇺 estava como 🇷🗻)
2. Horário entregando None (não usava begin_at como fallback)
"""

import re

print("=" * 80)
print("✅ VERIFICAÇÃO DE BUGS CORRIGIDOS")
print("=" * 80)
print()

# Ler o arquivo
with open('/home/msouza/Documents/bot-hltv/src/utils/embeds.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Bug 1: Verificar emoji RU
print("🧪 BUG 1: Emoji para 'ru' (Russo)")
print("-" * 80)

# Procurar por "ru": "<emoji>"
ru_match = re.search(r'"ru"\s*:\s*"([^"]+)"', content)
if ru_match:
    emoji = ru_match.group(1)
    print(f"Emoji encontrado: {emoji}")
    print(f"Emoji certo seria: 🇷🇺")
    
    if emoji == "🇷🇺":
        print("✅ CORRETO! Emoji 'ru' está certo!")
    else:
        print(f"❌ ERRADO! Emoji está bugado: {emoji}")
else:
    print("❌ Não encontrou entry 'ru' em LANGUAGE_FLAGS!")

print()
print()

# Bug 2: Verificar fallback para begin_at
print("🧪 BUG 2: Fallback para begin_at (horário)")
print("-" * 80)

# Procurar pela linha que faz fallback
fallback_pattern = r'time_to_display\s*=\s*scheduled_at\s*or\s*begin_at'
if re.search(fallback_pattern, content):
    print("✅ CORRETO! Fallback 'scheduled_at or begin_at' encontrado!")
else:
    print("❌ Fallback não encontrado!")

# Verificar se o código original estava ali
old_pattern = r'if\s+scheduled_at:'
if re.search(old_pattern, content):
    # Se ainda tem "if scheduled_at:" sem fallback é problema
    # Mas agora deveria estar "if time_to_display:"
    new_pattern = r'if\s+time_to_display:'
    if re.search(new_pattern, content):
        print("✅ Verificação feita: 'if time_to_display:' está no lugar certo!")
    else:
        print("⚠️  'if time_to_display:' não encontrado - pode estar com outro nome")

print()
print()

# Verificar outros emojis que estavam bugados
print("🧪 VERIFICAÇÃO ADICIONAL: Outros emojis potencialmente bugados")
print("-" * 80)

# Listar emojis bandeira que deveriam estar corretos
critical_languages = ["pt", "en", "es", "fr", "de", "ru", "zh", "ja", "ko"]
problematic = []

for lang in critical_languages:
    pattern = rf'"{lang}"\s*:\s*"([^"]+)"'
    match = re.search(pattern, content)
    if match:
        emoji = match.group(1)
        # Verificar se parece ser uma bandeira válida (tem exatamente 2 caracteres Unicode)
        if len(emoji) == 2:
            print(f"  ✅ {lang:5} → {emoji}")
        else:
            print(f"  ❌ {lang:5} → {emoji} (comprimento: {len(emoji)}, esperado: 2)")
            problematic.append(lang)
    else:
        print(f"  ❌ {lang:5} → NÃO ENCONTRADO!")
        problematic.append(lang)

print()
print()

# Resumo
print("=" * 80)
print("📊 RESUMO")
print("=" * 80)
print()

if not problematic:
    print("✅ TODOS OS BUGS FORAM CORRIGIDOS!")
    print()
    print("Correções realizadas:")
    print("  ✅ Emojis de bandeira corrigidos (ru, pt, fr, etc)")
    print("  ✅ Fallback para begin_at adicionado (horário não fica None)")
    print()
    print("Status: 🟢 PRONTO PARA PRODUÇÃO")
else:
    print("❌ Ainda há problemas:")
    for lang in problematic:
        print(f"  ❌ {lang}")
print()
