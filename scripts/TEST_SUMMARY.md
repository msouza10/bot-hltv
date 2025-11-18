# 🧪 Resumo dos Scripts de Teste

## Visão Geral

| Script | Objetivo | Tempo | Entrada |
|--------|----------|-------|---------|
| `test_youtube_service.py` | Testar com URLs públicas | 10s | Nenhuma |
| `test_youtube_real_data.py` | Testar com dados do banco | 5-10s | DB precisa ter dados |
| `run_complete_test.py` | Teste end-to-end completo | 35s | Nenhuma (faz tudo) |

---

## 🚀 Quick Start

### Opção 1: Teste Rápido (sem dados)
```bash
python scripts/test_youtube_service.py
```
✅ Rápido, não precisa de banco populado

### Opção 2: Teste com Dados Reais
```bash
# Abra um terminal e deixe o bot rodando
python -m src.bot

# Em outro terminal, execute teste após 30 segundos
python scripts/test_youtube_real_data.py
```

### Opção 3: Teste Completo Automático (Recomendado)
```bash
python scripts/run_complete_test.py
```
✅ Faz tudo automaticamente

---

## 📊 O Que Cada Um Testa

```
test_youtube_service.py
├── Videos YouTube (watch?v=...)
├── URLs curtas (youtu.be/...)
├── Handles (@channel)
├── Custom URLs (c/channel)
└── Fallback automático

test_youtube_real_data.py
├── Conecta ao banco
├── Busca URLs reais do YouTube
├── Testa cada URL
├── Mostra atualizações necessárias
└── Compara com dados armazenados

run_complete_test.py
├── Reset banco
├── Inicia bot (30s)
├── Coleta dados
├── Para bot
└── Executa test_youtube_real_data.py
```

---

## 📈 Interpretando Saída

### test_youtube_service.py
```
[1/5] Testando: Video (Rick Roll)
      URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
      Canal: Rick Astley
      ✅ PASSOU
```
✅ Funcionando perfeitamente

### test_youtube_real_data.py
```
[1/3] Match ID: 1269370
      URL: https://www.youtube.com/watch?v=CuHkkYAiPcM
      Canal atual no DB: YouTube
      🎥 Nome real obtido: ESL Counter-Strike
      ✅ DIFERENTE - Deveria ser atualizado
```
✅ Conseguiu extrair nome melhor do que o armazenado

### run_complete_test.py
```
📊 RESUMO DOS TESTES
✅ Sucessos:  8
❌ Falhas:    2
🎯 Taxa de sucesso: 80.0%
```
✅ Maioria dos testes passou

---

## ⚙️ Setup Necessário

### 1. YouTube API Key (Obrigatório para testes completos)
```bash
# Obtenha em: https://console.cloud.google.com/
# 1. Crie projeto
# 2. Ative YouTube Data API v3
# 3. Crie API Key
# 4. Adicione ao .env:

echo "YOUTUBE_API_KEY=sua_chave_aqui" >> .env
```

### 2. Banco de Dados
```bash
# Initialize
python -m src.database.build_db

# Verificar
ls -lah data/bot.db
```

---

## 🔍 Como Funciona Internamente

```
URL YouTube
    ↓
[YouTubeService.get_channel_name()]
    ├─ Se tem API Key
    │  ├─ Extrai Video ID
    │  ├─ Chama YouTube Data API v3
    │  └─ Retorna canal
    └─ Se sem API Key
       ├─ Tenta extrair da URL
       └─ Retorna canal ou fallback
```

---

## 🛠️ Troubleshooting

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: 'src'` | Rode do diretório raiz: `cd bot-hltv` |
| `YOUTUBE_API_KEY não configurada` | Adicione ao `.env` |
| `No such file 'data/bot.db'` | Execute: `python -m src.database.build_db` |
| `YouTube API limit exceeded` | Espere até amanhã (quota diária) |

---

## 📋 Checklist Completo

- [ ] YouTube API Key configurada
- [ ] `.env` tem a chave
- [ ] Banco inicializado
- [ ] Bot pode rodar sem erros
- [ ] `test_youtube_service.py` passa 40%+
- [ ] `test_youtube_real_data.py` encontra streams
- [ ] `run_complete_test.py` completa com sucesso

---

## 💾 Arquivos Criados

```
scripts/
├── test_youtube_service.py       # Teste com URLs públicas
├── test_youtube_real_data.py     # Teste com dados do DB
├── run_complete_test.py          # Teste end-to-end
├── README_TESTS.md               # Documentação detalhada
└── TEST_SUMMARY.md              # Este arquivo
```

---

## 🎯 Próximos Passos

1. ✅ Execute um teste (qualquer um)
2. ✅ Verifique se URL/API está correta
3. ✅ Resolva qualquer erro
4. 🚀 Deploy para produção
5. 📊 Monitor os logs

---

## 📞 Suporte

Se tiver problemas:

1. Verifique os logs:
   ```bash
   tail -f logs/bot.log | grep -i youtube
   ```

2. Teste apenas a API:
   ```bash
   python scripts/test_youtube_service.py
   ```

3. Verifique YouTube API Key:
   ```bash
   echo $YOUTUBE_API_KEY
   ```

4. Resete tudo:
   ```bash
   rm -f data/bot.db
   python -m src.database.build_db
   ```
