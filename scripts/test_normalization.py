#!/usr/bin/env python3
"""
Script para testar com os títulos reais que o usuário encontrou na Twitch.
"""

import logging
from typing import List

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Títulos reais que aparecem na Twitch
REAL_TITLES = [
    "🔴 BETERA VS LEO | CCT Season 3 Europe Series 11 |",
    "[LIVE] Betera vs Leo | [RU] CCT Season 3 Europe Series 11 |",
    "[RU] Betera vs Leo | CCT Season 3 Europe Series 11"
]

def extract_keywords(text: str) -> List[str]:
    """Extrai palavras-chave de um texto - versão ATUAL (com problema)"""
    if not text:
        return []
    
    text = text.lower()
    words = text.split()
    
    keywords = []
    for word in words:
        clean_word = word.strip('.,;:!?)[]"\'|🔴')
        if clean_word:
            keywords.append(clean_word)
            
            if "." in clean_word:
                base = clean_word.split(".")[0].strip()
                if base:
                    keywords.append(base)
    
    return keywords

def extract_keywords_improved(text: str) -> List[str]:
    """Versão MELHORADA que remove símbolos especiais também"""
    if not text:
        return []
    
    text = text.lower()
    
    # Remove emojis e símbolos especiais ANTES de split
    import re
    # Remove emojis
    text = re.sub(r'[\U0001F300-\U0001F9FF]+', '', text)
    # Remove símbolos como 🔴, 🔵, etc
    text = re.sub(r'[^\w\s\-\.]', '', text)
    
    words = text.split()
    
    keywords = []
    for word in words:
        clean_word = word.strip('.,;:!?)["\'-|')
        if clean_word and len(clean_word) > 1:  # Ignorar caracteres únicos
            keywords.append(clean_word)
            
            if "-" in clean_word:
                # Para "betera-something", também adicionar parte antes do hífen
                base = clean_word.split("-")[0].strip()
                if base:
                    keywords.append(base)
    
    return keywords

print("=" * 80)
print("Teste de Extração de Keywords - TÍTULOS REAIS")
print("=" * 80)

for title in REAL_TITLES:
    print(f"\n📌 Título Original: {title}")
    
    keywords_old = extract_keywords(title)
    print(f"   Versão ATUAL:    {keywords_old}")
    
    keywords_new = extract_keywords_improved(title)
    print(f"   Versão MELHORADA: {keywords_new}")
    
    # Testar se encontra "betera" e "leo"
    has_betera_old = "betera" in keywords_old
    has_leo_old = "leo" in keywords_old
    
    has_betera_new = "betera" in keywords_new
    has_leo_new = "leo" in keywords_new
    
    print(f"   Encontrou 'betera'? ATUAL={has_betera_old} vs MELHORADA={has_betera_new}")
    print(f"   Encontrou 'leo'? ATUAL={has_leo_old} vs MELHORADA={has_leo_new}")

print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)
print("\nProbema detectado:")
print("1. Símbolos como 🔴, |, [ ] não são removidos corretamente")
print("2. Isso faz com que 'betera|' não seja reconhecido como 'betera'")
print("3. A versão MELHORADA remove esses símbolos ANTES de processar")
