# 🎴 Quick Reference Card

## 🚀 Start Now (3 min)

```bash
pip install -r requirements.txt
python scripts/init_db.py
cp .env.example .env
# Editar .env com token
python -m src.bot
```

---

## 📂 Pastas Principais

| Pasta | O Quê | Mexer? |
|-------|-------|--------|
| `src/` | Código bot | Sim |
| `scripts/` | Ferramentas | Não (por enquanto) |
| `docs/` | Documentação | Referência |
| `data/` | Banco DB | NÃO! |
| `logs/` | Logs | Ler se tiver erro |

---

## 📄 Arquivos Principais

| Arquivo | Uso |
|---------|-----|
| `README.md` | Leia primeiro |
| `SETUP.md` | Setup detalhado |
| `COMECE_AQUI.md` | Este arquivo é mais rápido! |
| `.env` | Seus tokens (não commitar) |
| `requirements.txt` | pip install -r |

---

## 🎮 Comandos Discord

```
/partidas N         → Próximas N partidas
/aovivo             → Partidas ao vivo agora  
/resultados M N     → Últimos N resultados da liga M
```

---

## 🛠️ Scripts Úteis

```bash
# Verificar tudo OK
python scripts/check_status.py

# Validar cache (precisa estar ok)
python scripts/validate_cache_full.py

# Ver embeds formatados
python scripts/preview_embed.py

# Setup (primeira vez)
python scripts/init_db.py
```

---

## 📚 Documentação Rápida

```
Começar → README.md → docs/COMECE_AQUI.txt → docs/PRIMEIROS_PASSOS.md
Entender → docs/VISAO_GERAL.md → docs/ARQUITETURA_CACHE.md
Testar → docs/GUIA_TESTE_FINAL.md → scripts/
Debug → python scripts/check_status.py → logs/
Índice → docs/INDEX.md ou ESTRUTURA_VISUAL.md
```

---

## 🔍 Estrutura de Código

```
src/
├── bot.py                      ← Entrada
├── cogs/matches.py             ← Comandos /partidas, /aovivo, /resultados
├── database/cache_manager.py   ← Cache (memory → DB → API)
├── services/pandascore_service.py ← API
└── utils/embeds.py             ← Discord embeds
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Bot não inicia | Verificar `.env` com token |
| Sem partidas | `python scripts/init_db.py` |
| Erro na API | `python scripts/check_api_structure.py` |
| Falta dados | `python scripts/validate_cache_full.py` |
| Embeds errado | `python scripts/preview_embed.py` |

---

## ⚙️ Configuração

### .env (copiar de .env.example)
```env
DISCORD_TOKEN=seu_token_discord
PANDASCORE_TOKEN=seu_token_pandascore
DISCORD_GUILD_ID=opcional
```

---

## 📊 Cache

- **O quê**: 106 partidas CS2
- **Onde**: `data/bot.db` (SQLite)
- **Atualiza**: A cada 15 min
- **Tem**: Futuras, ao vivo, finalizadas, canceladas

---

## 🔗 Links Rápidos

| Documento | Localização |
|-----------|------------|
| Overview | `docs/VISAO_GERAL.md` |
| Arquitetura | `docs/ARQUITETURA_CACHE.md` |
| Spec Técnica | `docs/ESPECIFICACAO_TECNICA.md` |
| Como Testar | `docs/GUIA_TESTE_FINAL.md` |
| Índice | `docs/INDEX.md` |

---

## 💡 Tips

- `logs/` mostra erros (veja se falhar)
- `data/bot.db` é sagrado (NÃO deletar)
- `.env` tem tokens (NÃO commitar)
- `src/` é o código (modifique aqui)
- `scripts/` é para testar (não é essencial)

---

## ✅ Checklist Básico

- [ ] Clone repo
- [ ] `pip install -r requirements.txt`
- [ ] `cp .env.example .env` e editar
- [ ] `python scripts/init_db.py`
- [ ] `python -m src.bot`
- [ ] Testar em Discord: `/resultados 1 5`

---

## 🚀 Deploy

1. Ter `.env` configurado
2. `pip install -r requirements.txt`
3. `python scripts/init_db.py`
4. `python -m src.bot`

---

## 📞 Mais Info

```
Iniciante?       → Leia README.md
Developer?       → Leia docs/ESPECIFICACAO_TECNICA.md
Estrutura?       → Veja ESTRUTURA_VISUAL.md
Tudo?            → Vá a docs/INDEX.md
Scripts?         → Veja scripts/README.md
Precisa ajuda?   → python scripts/check_status.py
```

---

**Versão**: 3.0  
**Status**: ✅ Pronto para usar

Para começar: `python -m src.bot` 🎉
