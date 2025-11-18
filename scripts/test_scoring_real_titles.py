#!/usr/bin/env python3
"""
Script para testar o scoring com os títulos reais que o usuário encontrou.
"""

from typing import List

# Títulos reais que aparecem na Twitch
REAL_TITLES = [
    "🔴 BETERA VS LEO | CCT Season 3 Europe Series 11 |",
    "[LIVE] Betera vs Leo | [RU] CCT Season 3 Europe Series 11 |",
    "[RU] Betera vs Leo | CCT Season 3 Europe Series 11"
]

CHAMPIONSHIP = "CCT Europe"
TEAM1 = "Betera Esports"
TEAM2 = "Leo Team"

def extract_keywords(text: str) -> List[str]:
    """Extrai palavras-chave de um texto."""
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

def calculate_relevance_score(title: str, championship: str, team1: str, team2: str) -> int:
    """
    Calcula score de relevância do título.
    Retorna score baseado em palavras encontradas.
    """
    score = 0
    title_keywords = extract_keywords(title)
    title_lower = title.lower()
    
    print(f"     Keywords do título: {title_keywords}")
    
    # Score por campeonato (cada palavra do campeonato)
    if championship:
        champ_keywords = extract_keywords(championship)
        print(f"     Keywords do campeonato: {champ_keywords}")
        for champ_word in champ_keywords:
            if champ_word in title_keywords:
                print(f"        ✓ Campeonato: encontrou '{champ_word}' +10 pts")
                score += 10
            elif champ_word in title_lower:
                print(f"        ✓ Campeonato: encontrou parcial '{champ_word}' +5 pts")
                score += 5
    
    # Score por time 1 (cada palavra do time)
    if team1:
        team1_keywords = extract_keywords(team1)
        print(f"     Keywords time 1: {team1_keywords}")
        for team1_word in team1_keywords:
            if team1_word in title_keywords:
                print(f"        ✓ Time 1: encontrou '{team1_word}' +20 pts")
                score += 20
            elif team1_word in title_lower and len(team1_word) > 3:
                print(f"        ✓ Time 1: encontrou parcial '{team1_word}' +10 pts")
                score += 10
    
    # Score por time 2 (cada palavra do time)
    if team2:
        team2_keywords = extract_keywords(team2)
        print(f"     Keywords time 2: {team2_keywords}")
        for team2_word in team2_keywords:
            if team2_word in title_keywords:
                print(f"        ✓ Time 2: encontrou '{team2_word}' +20 pts")
                score += 20
            elif team2_word in title_lower and len(team2_word) > 3:
                print(f"        ✓ Time 2: encontrou parcial '{team2_word}' +10 pts")
                score += 10
    
    return score

print("=" * 80)
print("Teste de Scoring com Títulos Reais")
print("=" * 80)
print(f"Campeonato: {CHAMPIONSHIP}")
print(f"Time 1: {TEAM1}")
print(f"Time 2: {TEAM2}")
print()

for i, title in enumerate(REAL_TITLES, 1):
    print(f"\n{i}. Título: {title}")
    score = calculate_relevance_score(title, CHAMPIONSHIP, TEAM1, TEAM2)
    
    min_score = 10
    status = "✅ ACEITA" if score >= min_score else "❌ REJEITADA"
    print(f"   Score final: {score} {status}")

print("\n" + "=" * 80)
print("Conclusão")
print("=" * 80)
print("Se os scores acima forem >= 10, os títulos DEVERIAM ser aceitos!")
print("Se estão sendo rejeitados, há algo errado com o algoritmo real.")
