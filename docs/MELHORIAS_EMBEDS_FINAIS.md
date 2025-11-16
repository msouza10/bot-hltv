# 📋 Mudanças Implementadas nas Embeds

## ✅ O que foi adicionado

### 1. **Nomes dos Mapas** (antes era só "Mapa 1, 2, 3")
```
Antes: Mapa 1: 16-14
Depois: Mirage: 16-14
```
- Extrai `game.map.name` para mostrar o nome real do mapa

### 2. **Informações de Forfeit e Empate**
```
⚠️ Vitória por forfeit
🤝 Série empatada
```
- Detecta `match_data.forfeit`
- Detecta `match_data.draw`

### 3. **Versão do Jogo**
```
🎮 Versão: CS2
```
- Mostra `videogame_version` em ambas embeds

### 4. **Partida Remarcada**
```
🔄 Partida remarcada
```
- Detecta `match_data.rescheduled`

### 5. **Tipo de Partida Completo**
```
📋 Tipo: Eliminatória
```
- Mostra `match_type` (playoff, group stage, etc)

### 6. **IDs dos Times** (para referência interna)
```
IDs: 123456 vs 789012
```
- Útil para análises e logs

### 7. **Timestamp no Footer**
```
Match ID: 1234 • PandaScore • Iniciado em 16/11 14:30 UTC
```
- Mostra quando a partida realmente começou

## 📊 Estrutura de Identificação (Apenas pelo STATUS)

```python
# Lógica usada para identificar quando partida iniciou/terminou:

if status == "not_started":
    → Partida ainda não começou
    
if status == "running":
    → Partida está acontecendo AGORA
    
if status == "finished":
    → Partida já terminou
    
if status == "canceled":
    → Partida foi cancelada
    
if status == "postponed":
    → Partida foi adiada
```

**NÃO usa `begin_at`/`end_at` para lógica** - apenas para exibição de timestamps.

## 📁 Arquivos Modificados

- `src/utils/embeds.py`:
  - `create_result_embed()` - Adiciona informações extras
  - `create_match_embed()` - Melhorias para consistência

## 🎯 Informações da API Utilizadas

### Para FINISHED:
```python
✅ results[].score      → Placar (1-0, 2-1, etc)
✅ games[].teams[].score  → Score de cada mapa
✅ games[].map.name       → Nome do mapa (NEW!)
✅ forfeit              → Vitória por forfeit (NEW!)
✅ draw                 → Série empatada (NEW!)
✅ videogame_version    → Versão do jogo (NEW!)
✅ rescheduled          → Foi remarcada (NEW!)
✅ match_type           → Tipo (NEW!)
✅ begin_at             → Quando começou
✅ league               → Informações da liga
✅ serie                → Informações da série
✅ tournament           → Torneio
```

### Para NOT_STARTED / RUNNING:
```python
✅ status               → Estado atual
✅ scheduled_at         → Horário marcado
✅ begin_at             → Quando começou (RUNNING)
✅ videogame_version    → Versão do jogo (NEW!)
✅ rescheduled          → Foi remarcada (NEW!)
✅ match_type           → Tipo (NEW!)
```

## 🔍 Campos da API que Poderiam Ser Usados no Futuro

```python
# Se precisar expandir ainda mais:
official_stream_url    → Link da stream oficial
live_url              → URL para assistir
detailed_stats        → Estatísticas detalhadas
winner_id             → ID do time vencedor
league_id             → ID da liga
serie_id              → ID da série
modified_at           → Última modificação
original_scheduled_at → Horário original (se remarcada)
```
