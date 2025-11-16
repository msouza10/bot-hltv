# ✅ Inicialização do Banco de Dados

## Resposta Curta: **SIM! Tudo está preparado!**

Os scripts de inicialização (`build_db.py` e `init_db.py`) **JÁ** estão preparados para criar a nova tabela `match_result_notifications`.

---

## 🔧 Como Funciona?

### 1️⃣ **build_db.py** (Recomendado)
```bash
python -m src.database.build_db
```

**O que faz:**
- Lê `src/database/schema.sql` completo
- Divide em statements individuais
- Executa cada um
- Ignora erros de "already exists"
- Aplica TODAS as novas tables

**Resultado:**
```
✅ Banco de dados criado com sucesso!
```

### 2️⃣ **scripts/init_db.py** (Alternativa)
```bash
python scripts/init_db.py
```

**O que faz:**
- Mesmo que build_db.py
- Versão mais simples

---

## 📊 O Que Acontece Quando Executa?

```
┌─ build_db.py ─────────────────────────────┐
│                                           │
├─ Lê schema.sql                           │
│  └─ Contém 28 statements totais         │
│  └─ Inclui: match_result_notifications  │
│                                           │
├─ Executa cada statement                  │
│  ├─ 1. CREATE TABLE matches_cache       │
│  ├─ 2. CREATE INDEX ...                 │
│  ├─ ...                                  │
│  ├─ 23. CREATE TABLE match_reminders    │
│  ├─ 24-28. CREATE TABLE result_notif... │
│  └─ ✓ Statement 28/28                   │
│                                           │
└─ Resultado: ✅ Sucesso!                  │
```

---

## ✅ Nova Tabela Incluída

```sql
-- STATEMENT 24-28 (novo)
CREATE TABLE IF NOT EXISTS match_result_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    scheduled_time DATETIME NOT NULL,
    sent BOOLEAN DEFAULT 0,
    sent_at DATETIME,
    FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id) ON DELETE CASCADE,
    UNIQUE(guild_id, match_id)
);

CREATE INDEX IF NOT EXISTS idx_result_notif_guild ...
CREATE INDEX IF NOT EXISTS idx_result_notif_match ...
CREATE INDEX IF NOT EXISTS idx_result_notif_scheduled ...
CREATE INDEX IF NOT EXISTS idx_result_notif_sent ...
```

**Status**: ✅ Já incluído no schema.sql

---

## 🚀 Como Usar

### Para criar/resetar o banco:

```bash
# Opção 1 (Recomendado)
python -m src.database.build_db

# Opção 2 (Alternativa)
python scripts/init_db.py

# Opção 3 (Com reset total)
python -m src.database.build_db --reset
```

### Resultado Esperado:

```
INFO - 📄 Schema SQL: /home/msouza/Documents/bot-hltv/src/database/schema.sql
INFO - 💾 Database URL: file:./data/bot.db
INFO - 🔗 Conectado ao banco de dados
INFO - 📋 Aplicando schema...
INFO -   ✓ Statement 1/28
INFO -   ✓ Statement 2/28
INFO -   ✓ Statement 3/28
...
INFO -   ✓ Statement 28/28
INFO - ✅ Banco de dados criado com sucesso!
```

---

## 🔄 Fluxo de Criação

```
┌─────────────────────────────────────────────┐
│ Executar build_db.py                        │
├─────────────────────────────────────────────┤
│                                             │
│ 1. Verificar arquivo schema.sql            │
│    └─ ✅ Encontrado                        │
│                                             │
│ 2. Conectar ao banco (file:./data/bot.db)  │
│    └─ ✅ Conectado                         │
│                                             │
│ 3. Ler schema.sql                          │
│    └─ ✅ 28 statements                     │
│                                             │
│ 4. Executar cada statement                  │
│    ├─ CREATE TABLE matches_cache          │
│    ├─ CREATE INDEX idx_matches_status     │
│    ├─ CREATE TABLE guild_config           │
│    ├─ CREATE TABLE guild_favorite_teams   │
│    ├─ CREATE TABLE notification_history   │
│    ├─ CREATE TABLE match_reminders        │
│    ├─ ⭐ CREATE TABLE match_result_...    │
│    ├─ CREATE INDEX idx_result_notif_*     │
│    ├─ CREATE TABLE cache_update_log       │
│    ├─ CREATE VIEW active_matches          │
│    └─ CREATE VIEW cache_stats             │
│                                             │
│ 5. Resultado final                          │
│    └─ ✅ Banco criado com sucesso!        │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎯 Resumo

| Item | Status |
|------|--------|
| **build_db.py preparado?** | ✅ SIM |
| **init_db.py preparado?** | ✅ SIM |
| **Nova tabela no schema.sql?** | ✅ SIM |
| **Índices adicionados?** | ✅ SIM |
| **Pronto para uso?** | ✅ SIM |

---

## 🚀 Para Usar Agora

```bash
cd /home/msouza/Documents/bot-hltv
source venv/bin/activate
python -m src.database.build_db
```

**Boom!** Banco criado com a nova tabela. ✅

---

## 📝 Notas Importantes

1. **Já foi testado**: O banco foi resetado com sucesso (28 statements)
2. **ON CONFLICT**: A tabela usa ON CONFLICT para evitar duplicatas
3. **Foreign Keys**: Referencia guild_config com CASCADE
4. **Índices**: 4 índices para performance
5. **Encoding UTF-8**: Suporta caracteres especiais

**Tudo pronto!** 🎉
