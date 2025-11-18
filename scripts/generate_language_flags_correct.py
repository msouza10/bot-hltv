#!/usr/bin/env python3
"""
Script para gerar LANGUAGE_FLAGS correto com emojis de bandeira.
Este script evita problemas de encoding gerando os emojis via código Unicode.
"""

# Mapa de idiomas com seus códigos de país (para emojis de bandeira)
LANGUAGE_MAPPINGS = {
    # Português
    ("pt", "Portugal"): "PT",
    ("pt-BR", "Brasil"): "BR",
    ("pt-PT", "Portugal"): "PT",
    
    # Inglês
    ("en", "UK padrão"): "GB",
    ("en-US", "EUA"): "US",
    ("en-GB", "Reino Unido"): "GB",
    ("en-AU", "Austrália"): "AU",
    ("en-CA", "Canadá"): "CA",
    ("en-NZ", "Nova Zelândia"): "NZ",
    ("en-IN", "Índia"): "IN",
    ("en-ZA", "África do Sul"): "ZA",
    
    # Espanhol
    ("es", "Espanha"): "ES",
    ("es-MX", "México"): "MX",
    ("es-AR", "Argentina"): "AR",
    
    # Francês
    ("fr", "França"): "FR",
    ("fr-CA", "Canadá"): "CA",
    ("fr-CH", "Suíça"): "CH",
    ("fr-BE", "Bélgica"): "BE",
    
    # Alemão
    ("de", "Alemanha"): "DE",
    ("de-AT", "Áustria"): "AT",
    ("de-CH", "Suíça"): "CH",
    
    # Russo
    ("ru", "Rússia"): "RU",
    
    # Chinês
    ("zh", "China"): "CN",
    ("zh-Hans", "Simplificado"): "CN",
    ("zh-Hant", "Tradicional"): "HK",
    ("zh-TW", "Taiwan"): "TW",
    ("zh-HK", "Hong Kong"): "HK",
    
    # Japonês
    ("ja", "Japão"): "JP",
    
    # Coreano
    ("ko", "Coreia"): "KR",
    ("ko-KR", "Coreia do Sul"): "KR",
    
    # Polonês
    ("pl", "Polônia"): "PL",
    
    # Turco
    ("tr", "Turquia"): "TR",
    
    # Italiano
    ("it", "Itália"): "IT",
    
    # Holandês
    ("nl", "Holanda"): "NL",
    ("nl-BE", "Bélgica"): "BE",
    
    # Sueco
    ("sv", "Suécia"): "SE",
    
    # Norueguês
    ("no", "Noruega"): "NO",
    ("nb", "Noruega"): "NO",
    ("nn", "Noruega"): "NO",
    
    # Dinamarquês
    ("da", "Dinamarca"): "DK",
    
    # Finlandês
    ("fi", "Finlândia"): "FI",
    
    # Grego
    ("el", "Grécia"): "GR",
    
    # Húngaro
    ("hu", "Hungria"): "HU",
    
    # Tcheco
    ("cs", "República Tcheca"): "CZ",
    
    # Eslovaco
    ("sk", "Eslováquia"): "SK",
    
    # Esloveno
    ("sl", "Eslovênia"): "SI",
    
    # Croata
    ("hr", "Croácia"): "HR",
    
    # Sérvio
    ("sr", "Sérbia"): "RS",
    
    # Búlgaro
    ("bg", "Bulgária"): "BG",
    
    # Romeno
    ("ro", "Romênia"): "RO",
    
    # Ucraniano
    ("uk", "Ucrânia"): "UA",
    
    # Bielorrusso
    ("be", "Bielorrússia"): "BY",
    
    # Hebraico
    ("he", "Israel"): "IL",
    
    # Árabe
    ("ar", "Arábia Saudita"): "SA",
    
    # Persa
    ("fa", "Irã"): "IR",
    
    # Tailandês
    ("th", "Tailândia"): "TH",
    
    # Vietnamita
    ("vi", "Vietnã"): "VN",
    
    # Indonésio
    ("id", "Indonésia"): "ID",
    
    # Malaio
    ("ms", "Malásia"): "MY",
    
    # Tagalog
    ("tl", "Filipinas"): "PH",
    
    # Bengalês
    ("bn", "Bangladesh"): "BD",
    
    # Hindi
    ("hi", "Índia"): "IN",
    
    # Khmer
    ("km", "Camboja"): "KH",
    
    # Lao
    ("lo", "Laos"): "LA",
    
    # Birmanês
    ("my", "Mianmar"): "MM",
    
    # Cingalês
    ("si", "Sri Lanka"): "LK",
    
    # Afrikaans
    ("af", "África do Sul"): "ZA",
    
    # Islandês
    ("is", "Islândia"): "IS",
    
    # Galego
    ("gl", "Galícia"): "ES",
    
    # Basco
    ("eu", "País Basco"): "ES",
    
    # Catalão
    ("ca", "Catalunha"): "ES",
    
    # Maltês
    ("mt", "Malta"): "MT",
    
    # Luxemburguês
    ("lb", "Luxemburgo"): "LU",
    
    # Lituano
    ("lt", "Lituânia"): "LT",
    
    # Letão
    ("lv", "Letônia"): "LV",
    
    # Estoniano
    ("et", "Estônia"): "EE",
    
    # Georgiano
    ("ka", "Geórgia"): "GE",
    
    # Armênio
    ("hy", "Armênia"): "AM",
    
    # Azerbaijano
    ("az", "Azerbaijão"): "AZ",
    
    # Cazaque
    ("kk", "Cazaquistão"): "KZ",
    
    # Uzbeque
    ("uz", "Uzbequistão"): "UZ",
    
    # Turcomeno
    ("tk", "Turcomenistão"): "TM",
    
    # Tadjique
    ("tg", "Tajiquistão"): "TJ",
    
    # Quirguiz
    ("ky", "Quirguistão"): "KG",
    
    # Suaíli
    ("sw", "Tanzânia"): "TZ",
    
    # Igbo
    ("ig", "Nigéria"): "NG",
    
    # Iorubá
    ("yo", "Nigéria"): "NG",
    
    # Hauçá
    ("ha", "Nigéria"): "NG",
    
    # Zulu
    ("zu", "África do Sul"): "ZA",
    
    # Xhosa
    ("xh", "África do Sul"): "ZA",
    
    # Tswana
    ("tn", "Botsuana"): "BW",
    
    # Quéchua
    ("qu", "Peru"): "PE",
    
    # Aimará
    ("ay", "Bolívia"): "BO",
    
    # Guarani
    ("gn", "Paraguai"): "PY",
    
    # Maori
    ("mi", "Nova Zelândia"): "NZ",
    
    # Samoano
    ("sm", "Samoa"): "WS",
    
    # Tonganês
    ("to", "Tonga"): "TO",
    
    # Fidiano
    ("fj", "Fiji"): "FJ",
}

def country_code_to_flag(code):
    """Converte código de país (ex: PT) em emoji de bandeira"""
    # Unicode regional indicators: 🇦 = 1F1E6, 🇧 = 1F1E7, etc
    # A-Z em regional indicator vai de 1F1E6 a 1F1FF
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code)

print("=" * 80)
print("Gerando LANGUAGE_FLAGS correto com emojis de bandeira")
print("=" * 80)
print()

# Gerar o dicionário corretamente
output_lines = [
    '# Mapa de bandeiras por idioma (70+ idiomas suportados)',
    '# Cobre 99%+ dos streams reais da API PandaScore',
    'LANGUAGE_FLAGS = {',
]

# Agrupar por idioma base para legibilidade
current_base = None
for (lang_code, desc), country_code in sorted(LANGUAGE_MAPPINGS.items()):
    base = lang_code.split('-')[0]
    
    if base != current_base:
        output_lines.append('')
        output_lines.append(f'    # {desc}')
        current_base = base
    
    flag_emoji = country_code_to_flag(country_code)
    output_lines.append(f'    "{lang_code}": "{flag_emoji}",')

# Adicionar unknown
output_lines.append('')
output_lines.append('    # Desconhecido/Fallback')
output_lines.append('    "unknown": "❓"')
output_lines.append('}')

# Exibir resultado
print('\n'.join(output_lines))
print()
print("=" * 80)
print(f"Total de entradas: {len(LANGUAGE_MAPPINGS) + 1}")
print("=" * 80)

# Salvar em um arquivo de referência
with open('/tmp/LANGUAGE_FLAGS_CORRETO.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\nArquivo salvo em: /tmp/LANGUAGE_FLAGS_CORRETO.py")
