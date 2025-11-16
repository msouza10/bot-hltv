# 📊 Comparação de APIs para Dados de CS2

## 🎯 Objetivo da Análise

Identificar a melhor fonte de dados para o bot de notificações de partidas de CS2, comparando:
- Cobertura de dados
- Limites e restrições
- Preços e planos
- Facilidade de integração
- Confiabilidade e qualidade dos dados

**Data da análise:** 15 de novembro de 2025

---

## 1️⃣ PandaScore API

### 📖 Descrição
API profissional focada em esports com cobertura de múltiplos jogos, incluindo Counter-Strike.

### 🌐 Website
- Documentação: https://developers.pandascore.co/docs
- Website: https://pandascore.co

### ✅ Pontos Fortes

#### Cobertura de Dados
- **Fixtures (Gratuito)**: Calendário de partidas, times, horários, formato (BO1/BO3), streams
- **Historical Data**: Estatísticas detalhadas pós-partida (requer plano pago)
- **Live Data**: Dados em tempo real via WebSockets (requer plano Pro Live)
- **CS2/CS:GO**: Suporte completo para Counter-Strike

#### Dados Disponíveis
```javascript
// Exemplo de dados de fixtures
{
  match: {
    id: 12345,
    name: "FURIA vs Vitality",
    scheduled_at: "2025-11-15T18:00:00Z",
    format: "bo3",
    status: "not_started",
    streams: [...],
    opponents: [
      { team: { name: "FURIA", ... } },
      { team: { name: "Vitality", ... } }
    ],
    tournament: {
      name: "BLAST Premier",
      tier: "s"
    }
  }
}
```

#### Planos Disponíveis
| Plano | Características | Preço |
|-------|----------------|--------|
| **Fixtures Only** | • Calendário de partidas<br>• Resultados finais<br>• Informações básicas | **GRATUITO** ✅ |
| **Historical** | • Fixtures +<br>• Estatísticas pós-partida<br>• Dados de jogadores | **Sob consulta** |
| **Pro Live** | • Historical +<br>• Dados ao vivo via WebSocket<br>• Frames e eventos | **Sob consulta** |

#### Limites de API
- **Rate Limiting**: Não especificado claramente na documentação pública
- **Autenticação**: Token de API necessário
- **Endpoints**: REST API bem documentada
- **WebSockets**: Disponível para dados ao vivo (plano Pro Live)

### ❌ Pontos Fracos
- ❌ Preços não públicos (necessário contato comercial)
- ❌ Dados detalhados e ao vivo requerem planos pagos
- ❌ Voltado para empresas (betting, fantasy, media)
- ❌ Pode ser excessivo para uso pessoal/hobbyista

### 💡 Adequação para o Projeto
- ✅ **Fixtures (gratuito)**: PERFEITO para o MVP
- ✅ Dados estruturados e confiáveis
- ✅ API REST bem documentada
- ⚠️ Dados ao vivo requerem plano pago
- ⚠️ Sem preços públicos

### 🎯 Avaliação Geral
**Nota: 9/10 (para o MVP usando plano gratuito)**

---

## 2️⃣ Liquipedia API

### 📖 Descrição
Wiki comunitária de esports baseada em MediaWiki com API pública.

### 🌐 Website
- API: https://liquipedia.net/counterstrike/api.php
- Terms of Use: https://liquipedia.net/api-terms-of-use

### ✅ Pontos Fortes

#### Cobertura de Dados
- **Partidas**: Informações sobre torneios, times, jogadores
- **Torneios**: Detalhes completos de eventos
- **Resultados**: Histórico de partidas
- **Wiki Content**: Acesso a todo conteúdo da wiki

#### Dados Disponíveis
- MediaWiki API (action=query)
- Páginas de torneios e times
- Calendários de eventos
- Resultados e placements

### Características
- **Gratuito**: ✅ Totalmente gratuito
- **API**: MediaWiki API padrão
- **Licença**: CC BY-SA 3.0 (conteúdo de texto)
- **Rate Limiting**: ✅ Restrito (proteger servidores)

### ❌ Pontos Fracos
- ❌ **Não é uma API REST estruturada** - É MediaWiki API (complexa)
- ❌ **Dados não estruturados** - Parsing de wikitext necessário
- ❌ **Rate limiting estrito** - Proteção agressiva contra abuse
- ❌ **Não é real-time** - Wiki atualizada manualmente
- ❌ **Complexidade**: Difícil extrair dados estruturados
- ❌ **Sem garantias de formato** - Estrutura pode mudar

### 💡 Adequação para o Projeto
- ⚠️ Possível, mas trabalhoso
- ❌ Requer parsing complexo de wikitext/HTML
- ❌ Dados não são em tempo real
- ❌ Rate limiting pode ser problemático
- ✅ Gratuito

### 🎯 Avaliação Geral
**Nota: 4/10 (muito trabalhoso, dados não estruturados)**

---

## 3️⃣ Biblioteca cs2api (NPM)

### 📖 Descrição
Busca por biblioteca NPM para acesso a dados de CS2.

### 🔍 Resultado da Pesquisa
❌ **Não encontrada biblioteca específica "cs2api" no NPM**

### Bibliotecas Similares Encontradas
Nenhuma biblioteca NPM específica foi identificada para acesso a dados de partidas competitivas de CS2.

### Alternativas NPM
Existem algumas bibliotecas relacionadas:
- **steam-api**: Para dados da Steam (não relacionado a partidas competitivas)
- **csgo-api**: Pode estar desatualizada (CS:GO, não CS2)

### 💡 Adequação para o Projeto
- ❌ Não existe

### 🎯 Avaliação Geral
**Nota: 0/10 (não existe)**

---

## 4️⃣ GameScoreKeeper API

### 📖 Descrição
Plataforma de dados de esports.

### 🌐 Website
- Website: https://gamescorekeeper.com
- Link fornecido: https://gamescorekeeper.com/api/cs-go (❌ 404 - página não encontrada)

### 🔍 Resultado da Pesquisa
❌ **Link da API retorna 404 (página não existe)**

### Informações do Site
- Empresa focada em dados de esports
- Produtos: Esports Data, Websites, Widgets
- Clientes: Fantasy Esports, Betting, Media, Tournament Organizers
- Documentação: https://docs.gamescorekeeper.com/

### ❌ Status Atual
- Link da API CS:GO não funciona
- Documentação não acessível publicamente
- Preços não disponíveis
- Necessário contato comercial

### 💡 Adequação para o Projeto
- ❌ Não foi possível avaliar (link quebrado)
- ⚠️ Aparenta ser voltado para empresas
- ⚠️ Sem informações públicas de API

### 🎯 Avaliação Geral
**Nota: N/A (não acessível para avaliação)**

---

## 🏆 RECOMENDAÇÃO FINAL

### 🥇 Opção Recomendada: **PandaScore API (Plano Fixtures - Gratuito)**

#### Justificativa:

#### ✅ Vantagens Decisivas:
1. **Plano gratuito robusto**
   - Calendário completo de partidas
   - Informações de times e torneios
   - Status de partidas
   - Links para streams
   - Sem custo

2. **Dados estruturados**
   - REST API bem documentada
   - JSON estruturado
   - Fácil de integrar
   - Tipos de dados claros

3. **Adequado para o MVP**
   - Notificações de partidas próximas ✅
   - Notificações de início de partida ✅
   - Resultados finais ✅
   - Informações de torneios ✅

4. **Escalabilidade**
   - Se precisar de dados ao vivo no futuro, pode migrar para plano pago
   - API profissional e confiável
   - Usada por empresas grandes

#### ⚠️ Limitações a Considerar:
- Dados ao vivo (live stats) requerem plano pago
- Estatísticas detalhadas pós-partida são pagas
- Rate limits não especificados (precisa testar)

---

## 📋 Comparação Resumida

| Critério | PandaScore | Liquipedia | cs2api | GameScoreKeeper |
|----------|-----------|------------|--------|-----------------|
| **Disponibilidade** | ✅ Sim | ✅ Sim | ❌ Não existe | ❌ Link quebrado |
| **Gratuito** | ✅ Fixtures | ✅ Sim | - | ❓ Desconhecido |
| **Dados Estruturados** | ✅✅✅ | ❌ | - | ❓ |
| **Facilidade de Uso** | ✅✅✅ | ⚠️ Difícil | - | ❓ |
| **Documentação** | ✅✅✅ | ⚠️ MediaWiki | - | ❌ |
| **Tempo Real** | 💰 Pago | ❌ | - | ❓ |
| **CS2 Support** | ✅ Sim | ✅ Sim | - | ❓ |
| **Rate Limits** | ⚠️ TBD | ⚠️ Restritivo | - | ❓ |
| **Adequação MVP** | ✅✅✅ | ⚠️ | - | ❓ |
| **Nota Final** | **9/10** | **4/10** | **0/10** | **N/A** |

---

## 🚀 Plano de Ação Recomendado

### Fase 1: Prototipação (Semana 1-2)
1. ✅ Criar conta na PandaScore
2. ✅ Obter token de API gratuito
3. ✅ Testar endpoints de fixtures
4. ✅ Implementar primeiro protótipo

### Fase 2: MVP (Semana 3-4)
1. Implementar coleta de dados do PandaScore
2. Sistema de cache local
3. Notificações básicas
4. Testar rate limits

### Fase 3: Otimização (Futuro)
1. Avaliar necessidade de dados ao vivo
2. Se necessário, considerar upgrade para plano pago
3. Ou implementar scraping do HLTV como fallback

---

## 📝 Notas Importantes

### Sobre PandaScore Fixtures (Gratuito):
- ✅ Suficiente para notificações de partidas próximas
- ✅ Suficiente para notificações de início
- ✅ Suficiente para resultados finais
- ❌ Não inclui estatísticas detalhadas ao vivo
- ❌ Não inclui updates de placar em tempo real

### Para Dados Ao Vivo (Futuro):
Se no futuro precisarmos de:
- Placar atualizado em tempo real
- Estatísticas de mapas
- K/D/A dos jogadores ao vivo

Teremos 2 opções:
1. **Upgrade para PandaScore Pro Live** (pago, sob consulta)
2. **Scraping do HLTV** (gratuito, mais trabalhoso, legal?)

---

## 🔗 Links Úteis

### PandaScore
- Docs: https://developers.pandascore.co/docs
- Signup: https://app.pandascore.co/signup
- API Reference: https://developers.pandascore.co/reference
- Slack Community: https://join.slack.com/t/pandascore/shared_invite/...

### Liquipedia
- API: https://liquipedia.net/counterstrike/api.php
- Terms: https://liquipedia.net/api-terms-of-use

### HLTV (Alternativa de Scraping)
- Website: https://www.hltv.org
- Matches: https://www.hltv.org/matches
- Results: https://www.hltv.org/results

---

## 🎯 Conclusão

**A PandaScore API com o plano gratuito "Fixtures Only" é a melhor opção para o MVP do projeto.**

É a solução que oferece o melhor equilíbrio entre:
- ✅ Gratuidade
- ✅ Qualidade dos dados
- ✅ Facilidade de integração
- ✅ Documentação
- ✅ Confiabilidade

Com essa escolha, podemos:
1. Começar o desenvolvimento imediatamente
2. Ter dados estruturados e confiáveis
3. Não gastar dinheiro na fase inicial
4. Escalar para planos pagos se necessário no futuro

---

**Próximos passos:** 
1. Criar conta na PandaScore
2. Testar API com requests de exemplo
3. Implementar primeiro protótipo de coleta de dados

**Atualizado em:** 15 de novembro de 2025
