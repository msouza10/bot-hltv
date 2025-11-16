# 🚀 Quick Start Guide - Bot HLTV

Guia rápido para começar o desenvolvimento do bot.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [ ] **Node.js** (versão 16.x ou superior)
- [ ] **npm** ou **yarn**
- [ ] **Git**
- [ ] **Editor de código** (VS Code recomendado)
- [ ] **Conta no Discord** (para criar o bot)

---

## 🎯 Passos Iniciais

### 1. Inicializar o Projeto

```bash
# Navegar para o diretório do projeto
cd /home/msouza/Documents/bot-hltv

# Inicializar package.json
npm init -y

# Criar estrutura de pastas
mkdir -p src/{commands,events,services,utils,database}
mkdir -p config

# Criar arquivos essenciais
touch src/index.js
touch .env
touch .gitignore
touch README.md
```

### 2. Instalar Dependências

```bash
# Dependências principais
npm install discord.js dotenv axios node-schedule

# Dependências de desenvolvimento
npm install --save-dev nodemon eslint
```

### 3. Configurar .gitignore

```gitignore
# Node
node_modules/
npm-debug.log
package-lock.json
yarn.lock

# Environment
.env
.env.local
.env.*.local

# Database
*.sqlite
*.db

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
```

### 4. Criar Bot no Discord Developer Portal

1. Acesse: https://discord.com/developers/applications
2. Clique em "New Application"
3. Dê um nome ao bot (ex: "HLTV Notifier")
4. Vá em "Bot" → "Add Bot"
5. Copie o Token (⚠️ NUNCA compartilhe!)
6. Em "Privileged Gateway Intents":
   - ✅ Presence Intent (opcional)
   - ✅ Server Members Intent (opcional)
   - ✅ Message Content Intent (se precisar ler mensagens)

### 5. Configurar Arquivo .env

```env
# Discord Bot Token
DISCORD_TOKEN=your_bot_token_here

# Discord IDs (para desenvolvimento)
CLIENT_ID=your_application_id
GUILD_ID=your_test_server_id

# Configurações do Bot
NODE_ENV=development
HLTV_UPDATE_INTERVAL=1800000
```

### 6. Criar Código Base (index.js)

```javascript
require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
  ]
});

client.once('ready', () => {
  console.log(`✅ Bot online como ${client.user.tag}`);
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;
  
  console.log(`Comando recebido: ${interaction.commandName}`);
});

client.login(process.env.DISCORD_TOKEN);
```

### 7. Adicionar Scripts no package.json

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "deploy-commands": "node src/deploy-commands.js"
  }
}
```

### 8. Testar Conexão

```bash
npm run dev
```

Você deve ver: `✅ Bot online como [Nome do Bot]#1234`

---

## 🔧 Próximos Passos Técnicos

### Investigar API do HLTV

```bash
# Testar biblioteca hltv (se existir)
npm install hltv

# Criar arquivo de teste
touch src/test-hltv.js
```

```javascript
// src/test-hltv.js
const HLTV = require('hltv');

async function testHLTV() {
  try {
    const matches = await HLTV.getMatches();
    console.log('✅ API funcionando!');
    console.log('Partidas encontradas:', matches.length);
  } catch (error) {
    console.error('❌ Erro ao acessar HLTV:', error.message);
  }
}

testHLTV();
```

```bash
node src/test-hltv.js
```

### Criar Primeiro Comando Slash

```bash
# Criar arquivo de comando
touch src/commands/ping.js
touch src/deploy-commands.js
```

```javascript
// src/commands/ping.js
const { SlashCommandBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ping')
    .setDescription('Responde com Pong!'),
  
  async execute(interaction) {
    await interaction.reply('🏓 Pong!');
  },
};
```

```javascript
// src/deploy-commands.js
const { REST, Routes } = require('discord.js');
require('dotenv').config();

const commands = [
  require('./commands/ping').data.toJSON(),
];

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

(async () => {
  try {
    console.log('🔄 Registrando comandos...');
    
    await rest.put(
      Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
      { body: commands },
    );

    console.log('✅ Comandos registrados!');
  } catch (error) {
    console.error('❌ Erro:', error);
  }
})();
```

```bash
# Registrar comando
npm run deploy-commands
```

### Testar Comando no Discord

1. Vá ao seu servidor de teste
2. Digite `/ping`
3. O bot deve responder com "🏓 Pong!"

---

## 📚 Estrutura de Arquivos Atual

```
bot-hltv/
├── docs/
│   ├── VISAO_GERAL.md
│   └── PESQUISA_API.md
├── plan/
│   ├── TODO.md
│   └── DUVIDAS.md
├── src/
│   ├── index.js
│   ├── deploy-commands.js
│   ├── commands/
│   │   └── ping.js
│   ├── events/
│   ├── services/
│   ├── utils/
│   └── database/
├── config/
├── .env
├── .gitignore
├── package.json
└── README.md
```

---

## ✅ Checklist de Progresso

### Setup Inicial
- [ ] Node.js instalado e funcionando
- [ ] Projeto inicializado com npm
- [ ] Dependências instaladas
- [ ] Bot criado no Discord Developer Portal
- [ ] Token do bot copiado para .env
- [ ] Bot adicionado ao servidor de teste

### Testes Básicos
- [ ] Bot conecta com sucesso
- [ ] Comando `/ping` funciona
- [ ] Logs aparecem no console

### Próximos Passos
- [ ] Testar biblioteca HLTV (se existir)
- [ ] Implementar scraping básico (alternativa)
- [ ] Criar comando `/partidas`
- [ ] Implementar sistema de cache

---

## 🆘 Troubleshooting Comum

### Erro: "Invalid Token"
- ✅ Verificar se o token está correto no .env
- ✅ Token deve começar com o formato correto
- ✅ Não deve ter espaços extras

### Erro: "Missing Intents"
- ✅ Adicionar intents necessários no código
- ✅ Habilitar intents privilegiados no portal

### Comando não aparece no Discord
- ✅ Executar `npm run deploy-commands` novamente
- ✅ Aguardar alguns minutos (cache do Discord)
- ✅ Verificar CLIENT_ID e GUILD_ID no .env

### Bot offline após alguns minutos
- ✅ Verificar logs de erro
- ✅ Garantir que process não está sendo terminado
- ✅ Usar `nodemon` para desenvolvimento

---

## 📖 Recursos Úteis

### Documentações
- [Discord.js Guide](https://discordjs.guide/)
- [Discord.js Docs](https://discord.js.org/)
- [Discord Developer Portal](https://discord.com/developers/docs)

### Comunidades
- Discord.js Server: https://discord.gg/djs
- HLTV Subreddit: r/GlobalOffensive

### Ferramentas
- [Discord Permissions Calculator](https://discordapi.com/permissions.html)
- [Embed Generator](https://discohook.org/)

---

## 📝 Próximas Leituras

1. 📄 `plan/TODO.md` - Lista completa de tarefas
2. 📄 `plan/DUVIDAS.md` - Questões a serem respondidas
3. 📄 `docs/PESQUISA_API.md` - Informações sobre APIs do HLTV

---

**Status**: Projeto inicializado ✅  
**Próximo milestone**: Testar coleta de dados do HLTV  
**Data**: 15 de novembro de 2025
