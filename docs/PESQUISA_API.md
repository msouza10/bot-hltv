# 🔍 Pesquisa: APIs e Dados do HLTV

## 📊 Resultado da Pesquisa Inicial

Data da pesquisa: 15 de novembro de 2025

---

## 1. HLTV.org - Análise do Site

### O que foi encontrado:
- ✅ HLTV.org é a principal fonte de dados de CS2 competitivo
- ✅ Possui seções para:
  - Partidas do dia (Today's Matches)
  - Resultados (Results)
  - Eventos/Torneios
  - Estatísticas de times e jogadores
  - Rankings
  - Notícias

### Estrutura de URLs Identificadas:
- Partidas: `https://www.hltv.org/matches`
- Resultados: `https://www.hltv.org/results`
- Eventos: `https://www.hltv.org/events`
- Times: `https://www.hltv.org/team/[id]/[name]`
- Partida específica: `https://www.hltv.org/matches/[id]/[name]`

---

## 2. API Oficial do HLTV

### Status:
❌ **Não existe API pública oficial documentada**

### Observações:
- O HLTV não disponibiliza uma API REST pública
- Não há documentação oficial de endpoints
- Tentativas de acessar endpoints não documentados podem violar os termos de serviço

---

## 3. Alternativas Identificadas

### 3.1 Web Scraping do HLTV.org

**Prós:**
- ✅ Acesso direto aos dados mais atualizados
- ✅ Controle total sobre quais dados coletar

**Contras:**
- ❌ Pode violar Terms of Service (precisa verificar)
- ❌ Vulnerável a mudanças no layout do site
- ❌ Rate limiting pode bloquear requisições excessivas
- ❌ Mais complexo de implementar e manter

**Ferramentas:**
- `cheerio` - Parse de HTML
- `puppeteer` - Navegador headless (para conteúdo dinâmico)
- `axios` - HTTP requests

### 3.2 APIs Não-Oficiais de Terceiros

Bibliotecas encontradas na comunidade:

#### a) HLTV-API (Node.js)
- **Pacote NPM**: `hltv` 
- **GitHub**: Possivelmente mantido pela comunidade
- **Status**: Precisa investigar se ainda é mantido

**Exemplo de uso potencial:**
```javascript
const HLTV = require('hltv');

// Buscar partidas
HLTV.getMatches().then(matches => {
  console.log(matches);
});
```

#### b) hltv-livescore (Node.js)
- Focado em dados de partidas ao vivo
- Status de manutenção: a verificar

### 3.3 RSS Feeds do HLTV

**Descoberta:**
- ✅ HLTV oferece RSS feed: `https://www.hltv.org/rss/news`
- ⚠️ Limitado apenas a notícias, não dados de partidas

---

## 4. Discord.js - Documentação Estudada

### Informações Coletadas:

#### Setup Básico do Bot:
```javascript
const { Client, Events, GatewayIntentBits } = require('discord.js');

const client = new Client({ 
  intents: [GatewayIntentBits.Guilds] 
});

client.once(Events.ClientReady, readyClient => {
  console.log(`Ready! Logged in as ${readyClient.user.tag}`);
});

client.login(process.env.DISCORD_TOKEN);
```

#### Intents Necessários para o Bot:
- `GatewayIntentBits.Guilds` - Acesso a servidores
- `GatewayIntentBits.GuildMessages` - Se precisar ler mensagens
- `GatewayIntentBits.MessageContent` - Conteúdo das mensagens (requer privilégio no portal)

#### Estrutura Recomendada:
```
discord-bot/
├── commands/        # Comandos slash
├── events/          # Event handlers
├── config.json      # Configurações (sem token!)
├── index.js         # Entry point
└── deploy-commands.js  # Registrar comandos
```

#### Sistema de Eventos:
- `Events.ClientReady` - Bot conectado
- `Events.InteractionCreate` - Comando executado
- `Events.GuildCreate` - Bot adicionado a servidor
- `Events.GuildDelete` - Bot removido de servidor

---

## 5. Recomendações Técnicas

### Abordagem Sugerida (Ordem de Prioridade):

#### 1️⃣ **Primeira Tentativa: Biblioteca NPM Não-Oficial**
- Investigar pacote `hltv` no NPM
- Testar se ainda funciona e é mantido
- Vantagem: Implementação mais rápida

#### 2️⃣ **Segunda Opção: Web Scraping Cauteloso**
- Implementar scraper respeitoso:
  - User-Agent identificável
  - Rate limiting (1 request a cada 30-60 segundos)
  - Cache agressivo de dados
- Monitorar ToS do HLTV

#### 3️⃣ **Terceira Opção: Dados Manuais/Semi-Automáticos**
- Para MVP, usar dados de eventos grandes apenas
- Atualização manual de partidas importantes
- Escala conforme necessário

### Sistema de Cache Obrigatório:
```javascript
{
  matches: {
    lastUpdated: Date,
    data: [...],
    ttl: 1800 // 30 minutos
  }
}
```

### Rate Limiting Recomendado:
- **Mínimo**: 30 segundos entre requisições
- **Ideal**: 60 segundos entre requisições
- **Horário de pico**: Aumentar para 120 segundos

---

## 6. Próximos Passos de Investigação

### Perguntas a Responder:
1. ✅ Existe biblioteca NPM `hltv` funcional?
   - Testar instalação
   - Verificar última atualização
   - Ler documentação/exemplos

2. ❓ Termos de Serviço do HLTV permitem scraping?
   - Ler https://www.hltv.org/terms
   - Verificar robots.txt
   - Procurar menções sobre uso automatizado

3. ❓ Como o HLTV carrega dados?
   - Inspecionar network requests
   - Identificar endpoints internos
   - Verificar se há GraphQL ou API interna

4. ❓ Frequência de atualização necessária?
   - Partidas são adicionadas com quanto tempo de antecedência?
   - Placares ao vivo atualizam a cada quanto tempo?

---

## 7. Riscos e Mitigações

### Risco 1: Bloqueio por HLTV
**Mitigação:**
- Implementar rate limiting agressivo
- User-Agent identificável com email de contato
- Cache local extensivo
- Monitorar response codes (429, 403)

### Risco 2: Mudanças no Site
**Mitigação:**
- Testes automatizados de scraping
- Logs detalhados de erros
- Fallback para modo degradado (dados do cache)
- Sistema de alertas para falhas

### Risco 3: Dados Inconsistentes
**Mitigação:**
- Validação de dados coletados
- Schema validation (Joi, Zod)
- Logs de anomalias
- Confirmação dupla de dados críticos

---

## 8. Código de Exemplo: Estrutura Básica

### Serviço HLTV (Conceitual):
```javascript
class HLTVService {
  constructor() {
    this.cache = new Map();
    this.lastRequest = null;
    this.minInterval = 30000; // 30 segundos
  }

  async getMatches() {
    // Verificar cache
    if (this.cache.has('matches')) {
      const cached = this.cache.get('matches');
      if (Date.now() - cached.timestamp < 1800000) { // 30 min
        return cached.data;
      }
    }

    // Rate limiting
    await this.respectRateLimit();

    // Fazer requisição (scraping ou API)
    const matches = await this.fetchMatches();

    // Cachear
    this.cache.set('matches', {
      data: matches,
      timestamp: Date.now()
    });

    return matches;
  }

  async respectRateLimit() {
    if (this.lastRequest) {
      const elapsed = Date.now() - this.lastRequest;
      if (elapsed < this.minInterval) {
        await this.sleep(this.minInterval - elapsed);
      }
    }
    this.lastRequest = Date.now();
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async fetchMatches() {
    // Implementar scraping ou chamada de API
    throw new Error('Not implemented');
  }
}
```

---

## 📝 Notas Adicionais

- **Ética**: Sempre respeitar o site de origem dos dados
- **Performance**: Cache é essencial para não sobrecarregar HLTV
- **Manutenibilidade**: Código modular para fácil troca de fonte de dados
- **Monitoramento**: Logs detalhados para debugar problemas de coleta

---

**Próxima atualização**: Após testar bibliotecas NPM e verificar ToS do HLTV  
**Responsável**: Desenvolvedor do projeto
