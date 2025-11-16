#!/usr/bin/env python3
"""
GUIA DE TESTE - Sistema de Logs Detalhados
Siga este guia passo a passo para verificar se tudo está funcionando
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GUIA DE TESTE - SISTEMA DE LOGS                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Este guia o ajudará a testar e verificar o novo sistema de logs detalhados
para notificações.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 REQUISITOS ANTES DE COMEÇAR

  ✓ Bot iniciado e conectado
  ✓ Canal de notificações configurado com: /canal-notificacoes canal:#notificacoes
  ✓ Acesso a uma partida futura
  ✓ Terminal aberto mostrando logs do bot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 1: VERIFICAR INICIALIZAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passo 1: Inicie o bot
  $ python src/bot.py

Passo 2: Procure nos logs por:
  ✅ "BOT CONECTADO como: HLTV Bot"
  ✅ "✅ Agendador de cache ATIVO"
  ✅ "🔄 Loop de lembretes INICIADO | Verificando a cada 1 minuto"
  ✅ "🚀 BOT PRONTO PARA USO"

Resultado esperado:
  ✅ Todos os 4 itens acima aparecem nos logs

Se não aparecer:
  ❌ Algo errou na inicialização
  ❌ Procure por "Error" nos logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 2: ATIVAR NOTIFICAÇÕES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passo 1: Execute no Discord:
  /notificacoes ativar:true

Passo 2: Procure nos logs por:
  ✅ "📋 Comando /notificacoes ativar:true em guild"
  ✅ "📊 Total de partidas em cache: X" (X deve ser > 0)
  ✅ "🚀 Iniciando agendamento de lembretes..."
  ✅ "📅 Partida XXXXX: Começa em"
  ✅ "✅ Agendado: 60min ANTES | Lembrete em:"
  ✅ "✓ Partida XXXXX: 5 lembretes agendados"
  ✅ "✅ Agendamento concluído! X partidas configuradas"

Resultado esperado:
  ✅ Você vê linhas mostrando cada partida sendo agendada
  ✅ Cada partida tem 5 lembretes (60, 30, 15, 5, 0 min)
  ✅ Total de partidas > 0

Se não aparecer:
  ❌ Cache vazio (nenhuma partida)
  ❌ Procure por "Error" ou "❌" nos logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 3: VERIFICAR LEMBRETES AGENDADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passo 1: Abra outro terminal e execute:
  python scripts/check_reminders_detailed.py

Passo 2: Procure por:
  ✅ "[1️⃣ LEMBRETES PENDENTES]"
  ✅ "Total de lembretes pendentes: X" (X deve ser > 0)
  ✅ "⏳ Partida XXXXX"
  ✅ "Falta: XXm XXs"
  ✅ "[3️⃣ RESUMO POR TIPO]"
  ✅ "🔔 60 minutos: X total"
  ✅ "📊 TOTAL: X lembretes"

Resultado esperado:
  ✅ Total de lembretes pendentes = partidas × 5
  ✅ Cada lembrete mostra quanto tempo falta
  ✅ Todos os 5 tipos (60, 30, 15, 5, 0) aparecem no resumo

Se não aparecer:
  ❌ "Nenhum lembrete pendente!" significa nada foi agendado
  ❌ Volta ao TESTE 2 e verifica agendamento

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 4: VERIFICAR CICLO DE VERIFICAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passo 1: Fique olhando para os logs do bot

Passo 2: A cada 1 minuto, procure por:
  ✅ "🔍 Verificando lembretes pendentes..."
  ✅ "⏰ VERIFICAÇÃO DE LEMBRETES | Total pendentes: X"
  ✅ "⏳ Partida XXXXX (60min): Faltam XXm XXs"
  ✅ "⏳ Partida XXXXX (30min): Faltam XXm XXs"

Resultado esperado:
  ✅ A cada minuto você vê uma nova verificação
  ✅ O tempo "falta" diminui a cada verificação
  ✅ Nenhum erro aparece

Se não aparecer:
  ❌ Volta ao TESTE 3 - verifica se lembretes foram agendados

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 5: VERIFICAR ENVIO DE LEMBRETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passo 1: Encontre uma partida que começa logo (5-10 min)

Passo 2: Aguarde até que falte ~1 minuto para a hora

Passo 3: Procure nos logs por:
  ✅ "🚀 ENVIANDO: Partida XXXXX - Lembrete de 5 minutos"
  ✅ "[NOTIF] Iniciando envio para guild"
  ✅ "[NOTIF] ✅ Guild encontrada"
  ✅ "[NOTIF] ✅ Canal encontrado"
  ✅ "[NOTIF] ✅ ENVIADA: Guild XXXXX | Partida XXXXX | MSG ID: XXXXX"
  ✅ "✅ Marcado como enviado: Partida XXXXX (5min)"

Resultado esperado:
  ✅ Mensagem aparece no Discord no canal de notificações
  ✅ Todos os logs [NOTIF] aparecem com ✅
  ✅ Nenhum erro é mostrado

Se não aparecer:
  ❌ "🚀 ENVIANDO" não aparece: Falta tempo ainda
  ❌ "[NOTIF] ❌ Guild não encontrada": Bot não vê o servidor
  ❌ "[NOTIF] ❌ Canal não configurado": Falta /canal-notificacoes
  ❌ "[NOTIF] ❌ Erro ao enviar": Erro específico nos logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTE 6: VERIFICAR FALHAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se algo não funcionou, procure por:

  ❌ "❌ Erro ao agendar" → Problema no agendamento
  ❌ "[NOTIF] ❌" → Problema no envio
  ❌ "Exception" → Erro não tratado
  ❌ "Error" → Algum erro geral

Copie a mensagem de erro completa e você terá o contexto exato do problema.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SE TODOS OS TESTES PASSAREM

Significado:
  ✅ Sistema de agendamento funciona
  ✅ Loop de verificação funciona
  ✅ Envio de mensagens funciona
  ✅ Canal está configurado
  ✅ Bot tem acesso ao Discord

Próximas ações:
  1. Aguarde um lembrete ser enviado naturalmente
  2. Verifique se aparece no Discord
  3. Se tudo OK, notificações estão 100% funcionando! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ SE ALGUM TESTE FALHAR

Documentação:
  - Leia docs/LOGS_DETALHADOS.md (Como interpretar os logs)
  - Leia docs/MUDANCAS_LOGS.md (O que foi mudado)
  - Leia docs/RESUMO_LOGS.md (Resumo visual)

Precisar de ajuda:
  - Use TESTE 6 para copiar mensagem de erro exata
  - Os logs agora têm CONTEXTO completo
  - Será fácil identificar EXATAMENTE o que falhou

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""")

input("Pressione ENTER para ler a documentação completa...")

docs = {
    "LOGS_DETALHADOS.md": "Como usar e interpretar os logs",
    "MUDANCAS_LOGS.md": "Detalhes técnicos das mudanças",
    "RESUMO_LOGS.md": "Resumo visual"
}

print("\nDocumentação disponível:")
for doc, desc in docs.items():
    print(f"  📄 {doc}: {desc}")

print("\n✅ Sistema de logs detalhados PRONTO PARA TESTAR!")
print("=" * 80)
