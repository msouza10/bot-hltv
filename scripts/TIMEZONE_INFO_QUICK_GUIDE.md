# 🌍 Novo Comando: `/timezone_info`

## Resumo Rápido

Um novo comando foi adicionado ao bot: **`/timezone_info`**

Este comando permite que qualquer membro do servidor visualize qual timezone está sendo usado pelo bot para exibir os horários das partidas.

---

## 💡 O Que Faz

### Entrada
```
/timezone_info
```
(Sem parâmetros - clique e execute)

### Saída Esperada

**Se timezone foi configurado:**
```
🌍 Timezone do Servidor
Este servidor está usando America/Sao_Paulo

📍 Informações do Timezone
Timezone: America/Sao_Paulo
Abreviação: BRST
Offset UTC: -03:00
Emoji: 🇧🇷

⏰ Hora Atual neste Timezone
Data: 27/01/2025
Horário: 15:42:30 BRST

📋 O que você vê?
• Partidas: Convertidas para BRST
• Notificações: Enviadas no horário BRST
• Lembretes: Usando BRST
• API: Continua usando UTC internamente

🔧 Alterar Timezone
Use /timezone para mudar o timezone do servidor.
```

**Se timezone NÃO foi configurado:**
```
🌍 Timezone Não Configurado
Este servidor ainda não tem um timezone configurado.

📌 O que fazer?
Use o comando /timezone para configurar o timezone do seu servidor.

Exemplo:
/timezone fuso_horario: America/Sao_Paulo

ℹ️ Por que configurar?
• Todos os horários das partidas serão exibidos no timezone do seu servidor
• As notificações serão enviadas no horário correto
• Os lembretes respeitarão sua zona horária
```

---

## 🎯 Quando Usar

✅ **Quer saber qual timezone o bot está usando?** → `/timezone_info`

✅ **Quer confirmar que a configuração funcionou?** → `/timezone_info`

✅ **Quer ver a hora atual no timezone do servidor?** → `/timezone_info`

❌ **Quer mudar o timezone?** → Use `/timezone` (comando existente)

---

## 🔍 Exemplos de Timezones

```
Brasil:           America/Sao_Paulo
Estados Unidos:   America/New_York, America/Los_Angeles, America/Chicago
Europa:           Europe/London, Europe/Paris, Europe/Berlin
Ásia:             Asia/Tokyo, Asia/Shanghai, Asia/Singapore
Austrália:        Australia/Sydney
```

---

## 📊 Comparação com `/timezone`

| Comando | Objetivo | Quem Pode | Parâmetros | Modifica |
|---------|----------|----------|-----------|----------|
| `/timezone` | Configurar | Admins | `fuso_horario` obrigatório | ✅ Sim |
| `/timezone_info` | Ver | Todos | Nenhum | ❌ Não |

---

## 🧪 Teste Agora

1. Abra seu servidor Discord
2. Execute: `/timezone_info`
3. Veja qual timezone está configurado
4. Se não estiver, use `/timezone America/Sao_Paulo`
5. Execute `/timezone_info` novamente para confirmar

---

## 🔗 Integração

Este comando é apenas para **visualização**. O timezone é realmente usado em:

- ✅ `/partidas` - Mostra horários das partidas convertidos
- ✅ `/aovivo` - Mostra partidas ao vivo com horário correto
- ✅ `/resultados` - Mostra resultados com timezone
- ✅ Notificações - Enviadas no horário do servidor
- ✅ Lembretes - Respeitam seu timezone

---

## 📍 Localização no Código

- **Arquivo:** `src/cogs/notifications.py`
- **Linhas:** 319-430
- **Tipo:** Slash command (Nextcord)
- **Status:** ✅ Pronto para produção

---

**Novo comando adicionado com sucesso!** ✅
