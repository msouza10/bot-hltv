# 🤔 Dúvidas e Questões do Projeto

Este arquivo contém todas as dúvidas e questões sobre o projeto que precisam ser respondidas antes da implementação.

---

## 📡 Questões sobre Fonte de Dados (HLTV)

### 1. API do HLTV
- ❓ **O HLTV possui uma API oficial pública?**
  - Se sim, qual a documentação?
  - Existem limitações de rate limiting?
  - É necessário autenticação/API key?

# resposta aqui - Não, o HLTV não possui uma API oficial pública documentada. Portanto, temos algumas alternativas a considerar.
1 - api pandascore, quero entender quais as limitações dela, precos e dados que temoos.
2 - api liquidpedia, quero entender quais as limitações dela, precos e dados que temos.
3 - lib cs2api , quero entender quais as limitações dela, precos e dados que temos.
4 - https://gamescorekeeper.com/api/cs-go , quero entender quais as limitações dela, precos e dados que temos.

quero saber qual e a melhor alternativa para coletar dados das partidas de CS2 competitivas, a mais completa e confiavel.
# end

### 2. Estrutura de Dados
- ❓ **Quais informações exatas das partidas devemos coletar?**
  - Times, placar, data/hora, evento, formato (BO1/BO3)?
  - Links para streams?
  - Estatísticas dos jogadores?

# reposta aqui - As informações mínimas necessárias são: Times, placar, data/hora, evento, formato (BO1/BO3) e links para streams.

- cronograma de partidas futuras com notificacoes antes do inicio e no momento, data e hora, times e jogadores envolvidos, evento e formato.
### caso tenhamos essa informacao.
- atualizacao em tempo real de partidas ao vivo com placar, mapas, estatisticas basicas.
- resultados finais de partidas com estatisticas basicas.
- link para stream se disponivel.
# end
  
- ❓ **Como identificar diferentes tipos de partidas?**
  - Qualifiers vs Playoffs vs Finals?
  - Partidas online vs LAN?
  - Como filtrar apenas partidas "oficiais" e excluir showmatches?

# resposta aqui - Podemos identificar os tipos de partidas através dos dados fornecidos pela fonte escolhida (API ou scraping). Normalmente, essas informações estão associadas ao evento ou torneio ao qual a partida pertence.

- se possivel quero ter esse negocio para entender oq e aquele campeonato ou no minimo o nivel dele, se e em lan ou nao.


### 3. Frequência de Atualização
- ❓ **Com que frequência devemos verificar novas partidas?**
  - A cada 5, 15, 30 minutos?
  - O intervalo deve ser diferente para partidas ao vivo vs próximas?
  - Como balancear entre ter dados atualizados e não sobrecarregar o servidor?

# resposta aqui - A frequência ideal seria a cada 15 minutos para partidas próximas e a cada 5 minutos para partidas ao vivo, garantindo dados atualizados sem sobrecarregar o servidor.

- vamos precisar entender como funciona esses rates limits, mas qualquer coisa vamos fazer raspagem a cada 15 minutos para todas as partidas e salvar em um cache ou banco de dados.

---

## 🔔 Questões sobre Sistema de Notificações

### 4. Tipos de Notificações
- ❓ **Quais tipos de notificações são prioritários?**
  - [ x] Partida começando em X horas
  - [ x] Partida começou agora (live)
  - [ x] Resultado final
  - [ ] Mudanças no lineup de times
  - [ x] Partidas adiadas/canceladas
  
- ❓ **Quanto tempo antes de uma partida devemos notificar?**
  - 1 hora? 3 horas? 24 horas?
  - Múltiplas notificações (ex: 24h antes + 1h antes)?

# respota aqui 

- 24h antes, 1h antes e no momento da partida.

talvez coloquemos algo para isso ser configuravel pelo usuario, para talvez o bot mandar mensagem para ele no momento que ele quiser.

# 


### 5. Formato das Mensagens
- ❓ **Qual o formato ideal das notificações?**
  - Embed com imagens e cores?
  - Mensagem simples de texto?
  - Incluir botões para links externos?

  # resposta aqui - O formato ideal seria utilizar embeds com imagens e cores para tornar as notificações mais atraentes e informativas.
  - ainda nao pensei sobre isso.
  # end
  
- ❓ **Devemos incluir reações/botões interativos?**
  - Botão "Me lembrar 30 min antes"?
  - Reações para "Assistir" / "Não tenho interesse"?

 # reposta aqui - No momento, não vejo necessidade de incluir botões interativos. Podemos considerar isso para versões futuras, mas para o MVP, focar em mensagens claras e informativas é mais importante.

 vamos ver oq consiguimos fazer depois, mas quero de inicio ter um botao para ir para live ou pelo menos um link para algum site que tenha a transmissao.

 #end


### 6. Filtros e Personalização
- ❓ **Qual o nível de personalização por servidor?**
  - Seguir times específicos apenas?
  - Filtrar por tier de evento (Major, S-Tier, A-Tier)?
  - Permitir configurar horários de silêncio (não notificar de madrugada)?

  # resposta aqui - A personalização deve incluir a opção de seguir times específicos, filtrar por tier de evento e configurar horários de silêncio para evitar notificações indesejadas.

  avmos analisar a complexidade disso depois.
  
- ❓ **Como lidar com diferentes fusos horários?**
  - Detectar automaticamente do servidor?
  - Deixar usuário configurar?
  - Sempre usar horário UTC?

  # respota aqui - 

  vamos identificar o fuso horario do servidor automaticamente e permitir que o usuario configure se quiser um fuso diferente.

---

## 🗄️ Questões sobre Persistência de Dados

### 7. Escolha do Banco de Dados
- ❓ **Qual banco de dados usar?**
  - SQLite (mais simples, arquivo local)?
  - PostgreSQL/MySQL (mais robusto)?
  - MongoDB (NoSQL)?
  - JSON local (apenas para protótipo)?

  # resposta aqui - Para o MVP, SQLite é uma boa escolha devido à sua simplicidade e facilidade de uso. Podemos migrar para um banco mais robusto no futuro, se necessário.

  vamos constuir pensando em um sqlite, para no futuro usar um turso ou postgres se precisar escalar.
  
- ❓ **Quais dados precisam ser persistidos?**
  - Configurações por servidor (guild_id, channel_id)
  - Lista de times favoritos por servidor
  - Histórico de partidas notificadas (para evitar duplicatas)
  - Cache de dados do HLTV

  # resposta aqui - Precisamos persistir as configurações por servidor, lista de times favoritos, histórico de partidas notificadas e cache de dados do HLTV para garantir eficiência e evitar duplicatas.

  precisaremos avaliar a necessidade de cada um desses dados conforme avançamos no desenvolvimento.

### 8. Gerenciamento de Dados
- ❓ **Por quanto tempo manter dados antigos?**
  - Histórico de notificações: 7 dias? 30 dias? Para sempre?
  - Quando limpar cache de partidas antigas?

  # resposta aqui - Histórico de notificações pode ser mantido por 30 dias para referência, enquanto o cache de partidas antigas pode ser limpo após 1 hora da partida ter terminado.

  diariamente vamos limpar o cache de partidas antigas a ideia e ter o maximo de coisas possivel atualizadas.
  
- ❓ **Como lidar quando o bot sai de um servidor?**
  - Deletar todas as configurações automaticamente?
  - Manter por X dias caso retorne?

 # resposta aqui - Quando o bot sai de um servidor, devemos deletar todas as configurações automaticamente para evitar acúmulo de dados desnecessários.

  vamos pensar em uma forma de econimizar espaco, esses dados teram que estar definidas pelo proprio server, de uma forma que nao vamos presigar guardar muita coisa.

---

## ⚙️ Questões Técnicas e de Implementação

### 9. Escalabilidade
- ❓ **Como garantir que o bot escale para múltiplos servidores?**
  - Um canal de notificações por servidor?
  - Como evitar spam se o bot estiver em 100+ servidores?
  - Precisa de sharding do Discord.js?

    # resposta aqui - Devemos implementar um canal de notificações por servidor e garantir que o bot respeite os limites de mensagens do Discord para evitar spam. Sharding pode ser considerado se o bot crescer significativamente.

    a ideia e ser um bot simples, privado e opensource, nao vou me preocupar com isso por enquanto.

### 10. Performance e Rate Limiting
- ❓ **Como respeitar os rate limits do Discord?**
  - Quantas mensagens por segundo podemos enviar?
  - Como enfileirar notificações se houver muitos servidores?
  
- ❓ **Como lidar com falhas temporárias?**
  - Retry logic: quantas tentativas?
  - Cache de fallback se HLTV estiver offline?

### 11. Comandos e Interação
- ❓ **Quais comandos são essenciais no MVP?**
  - `/setup` para configuração inicial?
  - `/partidas` para listar próximas?
  - `/seguir [time]` para adicionar favoritos?
  - `/parar` para desativar notificações?

  # respota aqui - Sim, esses comandos são essenciais para o MVP e devem ser implementados inicialmente.

  vamos adicionando novos comandos conforme necessario.
  
- ❓ **Comandos devem ser slash commands ou mensagens com prefixo?**
  - Apenas slash commands (moderna)?
  - Suportar ambos?

# reposta aqui - Devemos focar em slash commands para o MVP, pois são mais modernos e oferecem melhor experiência ao usuário.

ambos sao simples de implementar, mas quero focar em slash commands, vamos tentar ter os dois



### 12. Hospedagem e Deploy
- ❓ **Onde hospedar o bot?**
  - Heroku (free tier descontinuado)?
  - Railway / Render / Fly.io?
  - VPS próprio (DigitalOcean, AWS)?
  - Precisa estar 24/7 online?
  
# respota aqui - 

  PRecisamos pensar nisso ainda.

- ❓ **Custos estimados?**
  - Hospedagem: free tier suficiente?
  - Banco de dados: incluído ou separado?

---

## 🎯 Questões sobre Escopo do MVP

### 13. Definição do MVP (Minimum Viable Product)
- ❓ **O que DEVE estar no MVP (versão 1.0)?**
  - Sistema básico de notificações?
  - Suporte a times favoritos?
  - Apenas partidas ao vivo ou incluir próximas?

    # resposta aqui - O MVP deve incluir o sistema básico de notificações, suporte a times favoritos e incluir tanto partidas ao vivo quanto próximas.

    sistema de notificacoes basico incluir tanto partidas ao vivo quanto proximas.
  
- ❓ **O que pode ficar para versões futuras?**
  - Estatísticas de jogadores/times?
  - Suporte multi-idioma?
  - Sistema de rankings?
  - Notificações via DM?

    respota aqui - Estatísticas de jogadores/times, suporte multi-idioma, sistema de rankings e notificações via DM podem ser deixados para versões futuras, focando no core funcional do bot no MVP.

    respota via dm e legal, mas quero focar no core funcional do bot primeiro. as outras oicsas vamos ir fazendo comforme complexidade.

### 14. Prioridades
- ❓ **Qual a ordem de prioridade das features?**
  1. Sistema de notificação básico de partidas ao vivo?
  2. Notificação de partidas próximas (1h antes)?
  3. Sistema de times favoritos?
  4. Comandos de consulta (`/partidas`, `/resultados`)?
  5. Dashboard web (futuro)?

---

## 🔐 Questões de Segurança e Privacidade

### 15. Dados Sensíveis
- ❓ **Quais dados do usuário precisamos armazenar?**
  - Apenas guild_id e channel_id?
  - User_id para preferências individuais?
  
- ❓ **Como proteger o token do bot?**
  - `.env` + `.gitignore`?
  - Secrets management do host (Heroku Config Vars)?

### 16. Moderação e Spam
- ❓ **Como evitar que o bot seja usado para spam?**
  - Limitar comandos por usuário (rate limiting)?
  - Apenas admins podem configurar notificações?
  - Sistema de whitelist de servidores?

---

## 📝 Outras Questões

### 17. Documentação e Suporte
- ❓ **Onde hospedar documentação para usuários?**
  - GitHub README?
  - Site próprio?
  - Wiki do Discord?
  
- ❓ **Como usuários vão reportar bugs/sugerir features?**
  - GitHub Issues?
  - Servidor de suporte no Discord?
  - Formulário Google?

### 18. Licença e Open Source
- ❓ **O bot será open source?**
  - Se sim, qual licença (MIT, GPL)?
  - Como gerenciar contribuições?
  
- ❓ **Monetização futura?**
  - Bot será sempre gratuito?
  - Sistema de premium para features avançadas?

---

## ✍️ Instruções para Responder

Para cada dúvida acima, por favor forneça:
1. ✅ **Resposta direta**
2. 📌 **Justificativa** (se aplicável)
3. 🔗 **Links/Referências** (se houver)

Adicione novas dúvidas conforme surgirem durante o desenvolvimento!

---

## 🛠 Decisão Tecnológica (resumo)

- Linguagem escolhida: **Python 3.10+** (você indicou maior familiaridade com Python)
- Biblioteca Discord: **Pycord (py-cord) >=2.4** — moderna, com bom suporte a slash commands
- Motivo: produtividade do desenvolvedor, ecossistema assíncrono adequado (aiohttp/aiosqlite), e documentação suficiente para o MVP.

Próximos passos técnicos imediatos:
1. Criar venv e `requirements.txt` (conter py-cord, aiohttp, aiosqlite, APScheduler, python-dotenv)
2. Gerar tokens (PandaScore, Discord) e salvar em `.env` (usar `.env.example` como template)
3. Implementar client PandaScore e job de polling mínimo para validar chamadas reais

---

**Última atualização:** 15 de novembro de 2025
