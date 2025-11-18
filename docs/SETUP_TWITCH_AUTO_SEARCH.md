# 🚀 Setup: Sistema de Busca Automática Twitch

## 1. Preparar Credenciais Twitch

### Obter Client ID e Client Secret
1. Acesse: https://dev.twitch.tv/console/apps
2. Clique "Create Application"
3. Preencha:
   - **Name**: bot-hltv (ou seu nome)
   - **Application Type**: Confidential Client
   - **Category**: Application Integration
4. Clique "Create"
5. Copie **Client ID**
6. Clique "New Secret" e copie o **Client Secret**

### Adicionar ao `.env`
```env
TWITCH_CLIENT_ID=seu_client_id_aqui
TWITCH_CLIENT_SECRET=seu_client_secret_aqui
```

---

## 2. Atualizar Database Schema

```bash
# Navegar até o diretório do bot
cd /home/msouza/Documents/bot-hltv

# Ativar ambiente virtual
source venv/bin/activate

# Executar build_db para aplicar novo schema
python -m src.database.build_db
```

Esperado:
```
💾 Database URL: file:./data/bot.db
📋 Aplicando schema...
  ✓ Statement 1/X
  ✓ Statement 2/X
  ...
✅ Banco de dados criado com sucesso!
```

---

## 3. Iniciar o Bot

```bash
python -m src.bot
```

No log, procure por:
```
✓ Agendador iniciado com Discord Tasks!
  • Atualização completa: a cada 3 minutos
  • Verificação de resultados: a cada 1 minuto
  • Busca automática de streams: a cada 10 minutos  ← CONFIRMAÇÃO!
```

---

## 4. Testar Funcionamento

### Teste 1: Verificar streams automatizadas
```bash
# Em outro terminal, enquanto o bot está rodando:
python scripts/check_cache_content.py

# Procure por entradas com:
# is_automated: 1
# viewer_count: > 0
```

### Teste 2: Discord
1. Chamar `/partidas` ou `/aovivo`
2. Procurar por streams com emoji 🤖
3. Clicar no link para verificar se leva ao canal Twitch

---

## 5. Verificar Logs

```bash
# Terminal em tempo real
tail -f logs/bot.log | grep -i "🤖\|stream\|twitch"

# Procure por:
# 🤖 Iniciando busca automática de streams na Twitch...
# 🔍 Encontrados X matches sem streams
# ✅ Stream encontrada: [canal] (XXXX viewers)
```

---

## 📋 Checklist Final

- [ ] Credenciais Twitch adicionadas ao `.env`
- [ ] Database schema atualizado (`build_db.py` executado)
- [ ] Bot iniciado com sucesso
- [ ] Log mostra "Busca automática de streams: a cada 10 minutos"
- [ ] Streams com 🤖 aparecem nos embeds do Discord
- [ ] Links de streams funcionam quando clicados

---

## 🐛 Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: No module named 'libsql_client'` | `pip install -r requirements.txt` |
| `TypeError: get_twitch_search_service() got no arguments` | Verificar imports em cache_scheduler.py |
| `is_automated column not found` | Rodar `python -m src.database.build_db --reset` |
| Nenhuma stream encontrada (logs vazios) | Aguardar 10 minutos da inicialização ou verificar TWITCH_CLIENT_ID |
| `403 Unauthorized` na Twitch API | Verificar credenciais Twitch no .env |

---

## 📞 Suporte

Se tiver problemas:

1. **Verificar logs**: `tail -f logs/bot.log`
2. **Verificar configuração**: `cat .env | grep TWITCH`
3. **Resetar database** (cuidado - apaga dados):
   ```bash
   rm data/bot.db
   python -m src.database.build_db
   ```
4. **Reiniciar bot**: Ctrl+C e depois `python -m src.bot`

---

**Tudo pronto? Você está 100% operacional! 🎉**
