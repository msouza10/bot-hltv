# 🎯 Resumo: Como Identificar Status de Partida

## 📌 Regra Principal: **Use APENAS o campo `status`**

```python
status = match_data.get("status")

# Possíveis valores:
- "not_started"   → Futuro (ainda não começou)
- "running"       → Ao vivo (está acontecendo AGORA)
- "finished"      → Finalizado (terminou)
- "canceled"      → Cancelado
- "postponed"     → Adiado
```

---

## 📊 Informações por Status

### 1️⃣ **NOT_STARTED** (Futuro)
```
status = "not_started"
begin_at = data_futura (ex: 2025-11-17T10:00:00Z)
end_at = None
results = [0, 0] ou empty
games = lista de mapas planejados
```
**Mostra:** Horário agendado, times, torneio, formato

---

### 2️⃣ **RUNNING** (Ao Vivo)
```
status = "running"
begin_at = data_passada (já começou)
end_at = None (ainda não terminou)
results = pode ter scores parciais
games = mapas em progresso ou completos
```
**Mostra:** Times, placar parcial, mapa atual, torneio

---

### 3️⃣ **FINISHED** (Finalizado)
```
status = "finished"
begin_at = data_passada
end_at = pode ser None (API não preenche para CS2)
results = [score_time1, score_time2] com scores REAIS
games = todos os mapas com resultados (score, times)
```
**Mostra:**
- ✅ Placar final (com 🏆 vencedor)
- ✅ Detalhes de cada mapa com nomes (Mirage, Inferno, etc)
- ✅ Duração (se available)
- ✅ Se foi forfeit ou empate
- ✅ Versão do jogo
- ✅ Tipo de partida
- ✅ Se foi remarcada

---

### 4️⃣ **CANCELED** (Cancelado)
```
status = "canceled"
begin_at = None (foi cancelado antes de começar)
end_at = None
results = [0, 0]
games = lista de mapas que seria jogado
```
**Mostra:** ❌ Cancelado, times, torneio, motivo (se disponível)

---

### 5️⃣ **POSTPONED** (Adiado)
```
status = "postponed"
begin_at = None ou data_antiga
end_at = None
results = [0, 0]
games = não foi jogado
```
**Mostra:** 🔄 Adiado, times, torneio original

---

## 🔍 Campos Adicionais Utilizados

| Campo | Tipo | Quando Usar |
|-------|------|------------|
| `forfeit` | bool | Mostrar "Vitória por forfeit" se true |
| `draw` | bool | Mostrar "Série empatada" se true |
| `rescheduled` | bool | Mostrar "Partida remarcada" se true |
| `videogame_version` | string | Mostrar versão do jogo |
| `match_type` | string | Mostrar tipo (playoff, group stage, etc) |
| `games[].map.name` | string | Nome do mapa (Mirage, Inferno, etc) |

---

## ✨ Exemplo de Embed Completo (FINISHED)

```
✅ FaZe Clan 2 - 1 FaZe Rising
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Torneio
ESL Pro League
Season 20

📺 Formato          📅 Data
BO3                 16/11/2025 14:30

📊 Resultado dos Mapas
Mirage: 16-**14**
Inferno: **16**-13  
Bind: **16**-12

⏱️ Duração
1h 45m

ℹ️ Detalhes
🎮 Versão: CS2
📋 Tipo: Semifinal

🔗 Informações
[Stream] | [Detalhes] | CS:GO | IDs: 123 vs 456

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Match ID: 1267654 • PandaScore • Iniciado em 16/11 14:20 UTC
```

---

## 🛠️ Lógica na Prática

```python
def process_match(match_data: Dict):
    status = match_data.get("status")
    
    if status == "not_started":
        # Mostrar embed genérico com horário
        return create_match_embed(match_data)
    
    elif status == "running":
        # Mostrar embed com placar em tempo real
        return create_match_embed(match_data)
    
    elif status == "finished":
        # Mostrar embed COMPLETO com todos os detalhes
        return create_result_embed(match_data)
    
    elif status in ["canceled", "postponed"]:
        # Mostrar embed com aviso
        return create_result_embed(match_data)  # Mesma função, detecta status automaticamente
```

---

## 🎯 Conclusão

✅ **Simples:** Use apenas `status` para saber o estado
✅ **Completo:** Todas as informações extras já são capturadas
✅ **Consistente:** Mesma lógica em ambas embeds (matches e results)
✅ **Pronto:** Bot está live e rodando!
