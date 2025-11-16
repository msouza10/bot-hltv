# 🔧 Especificação Técnica — Bot HLTV (Python / Pycord)

Versão focada no stack Python (Pycord, aiohttp, APScheduler, aiosqlite). Este documento resume contratos, modelos de dados, schema de banco, fluxos de notificação e exemplos mínimos de implementação.

Última atualização: 15/11/2025

---

## 1. Objetivo

Entregar um bot de Discord que notifique servidores sobre partidas de CS2 nas janelas: 24h, 1h, quando iniciar (live) e quando terminar (resultado). O MVP usa PandaScore (Fixtures) via polling.

Critérios de sucesso (MVP):
- Enviar notificações corretas sem duplicidade
- Comandos básicos funcionais (/setup, /seguir, /partidas)
- Persistência mínima (SQLite)

---

## 2. Contrato com a PandaScore (cliente HTTP)

Base URL: https://api.pandascore.co

Autenticação: header Authorization Bearer <API_TOKEN>

Endpoints utilizados (exemplos):
- GET /csgo/matches/upcoming?per_page=50&sort=scheduled_at
- GET /csgo/matches/running
- GET /csgo/matches/past?per_page=20&sort=-end_at
- GET /csgo/matches/{match_id}

Respostas: JSON arrays ou objetos. Converter para modelos internos imediatamente. Tratar campos opcionais (logos, times sem slug, partidas adiadas).

Rate limits: planejar para 1000 req/h (plano gratuito). Implementar cache e backoff exponencial.

---

## 3. Modelos principais (Python dataclasses)

Arquivo sugerido: `src/models.py` ou `src/models/*.py`.

Exemplo mínimo:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class Team:
    id: int
    name: str
    slug: Optional[str]
    logo: Optional[str]

@dataclass
class Tournament:
    id: int
    name: str
    slug: Optional[str]

@dataclass
class MatchSummary:
    id: int
    status: str  # not_started, running, finished
    scheduled_at: Optional[datetime]
    opponents: List[Team]
    tournament: Optional[Tournament]
    best_of: Optional[int]
    raw: Dict  # payload cru para debug / cache
```

Comentários:
- Sempre manter o `raw` original para diagnóstico.
- Converter timestamps para UTC e armazenar em ISO.

---

## 4. Banco de Dados (SQLite) — schema mínimo

Arquivo: `data/schema.sql`

Tabelas essenciais:

```sql
CREATE TABLE IF NOT EXISTS guilds (
  guild_id TEXT PRIMARY KEY,
  notification_channel_id TEXT,
  language TEXT DEFAULT 'pt-BR',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorite_teams (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT NOT NULL,
  team_slug TEXT NOT NULL,
  team_name TEXT,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(guild_id, team_slug)
);

CREATE TABLE IF NOT EXISTS notifications_sent (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  guild_id TEXT NOT NULL,
  notification_type TEXT NOT NULL,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(match_id, guild_id, notification_type)
);

CREATE TABLE IF NOT EXISTS matches_cache (
  match_id INTEGER PRIMARY KEY,
  status TEXT NOT NULL,
  scheduled_at TIMESTAMP,
  data TEXT NOT NULL,
  cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Uso:
- `notifications_sent` evita duplicatas. Inserir com `INSERT OR IGNORE`.
- `matches_cache` mantém payloads para diminuir chamadas à API.

---

## 5. Scheduler e Polling

- Polling padrão: a cada 15 minutos, buscar próximas partidas (window: próximas 48h).
- Polling live: a cada 5 minutos para partidas com status `running` ou próximas a iniciar (ex.: < 1h).
- Usar APScheduler com jobs assíncronos ou combinar com loop asyncio.

Fluxo resumido do job:
1. Buscar `upcoming` e `running` da PandaScore
2. Para cada partida, converter para MatchSummary
3. Comparar com `matches_cache` e `notifications_sent`
4. Determinar quais notificações enviar (24h, 1h, live, finished)
5. Enviar embed via Pycord e registrar em `notifications_sent`

Janela de envio:
- 24h: enviar se scheduled_at estiver entre 23h e 25h (tolerância de 1h)
- 1h: enviar se scheduled_at estiver entre 50min e 70min

---

## 6. Formato de mensagens (Embeds)

- Mensagens com embed:
  - Título: `Team A x Team B`
  - Thumbnails: logos dos times quando disponíveis
  - Campos: torneio, horário (BRT/UTC), formato (BO3), links (PandaScore)
  - Botões: link para página do evento / streams (ActionRow com Button)

Padronizar cores por tipo: info (azul) — 24h, warning (laranja) — 1h, danger (vermelho) — live, success (verde) — final.

---

## 7. Cliente PandaScore (exemplo mínimo)

Arquivo: `src/services/pandascore_service.py`

```python
import aiohttp
import os
from typing import List

class PandaScoreClient:
    BASE = "https://api.pandascore.co"

    def __init__(self, token: str = None):
        self.token = token or os.getenv("PANDASCORE_API_KEY")
        self.session = None

    async def _session(self):
        if not self.session or self.session.closed:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def get_upcoming(self, per_page: int = 50):
        s = await self._session()
        async with s.get(f"{self.BASE}/csgo/matches/upcoming", params={"per_page": per_page}) as r:
            r.raise_for_status()
            return await r.json()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
```

Notas operacionais:
- Tratar exceções aiohttp.ClientError
- Implementar cache simples com TTL por partida
- Implementar backoff exponencial para 429/5xx

---

## 8. Tratamento de erros e resiliência

- Logar todas as falhas com contexto (match_id, guild_id)
- Retry limitado para chamadas externas (3 tentativas com backoff)
- Em caso de 429: aguardar X segundos conforme header `Retry-After`
- Validar campos obrigatórios antes de enviar notificações (opponents, scheduled_at)

---

## 9. Contrato das funções chave (inputs/outputs)

- `get_upcoming()` -> List[dict] (raw)
- `parse_match(raw)` -> MatchSummary
- `should_notify(match, guild_config)` -> List[str] (tipos de notificações: ['24h','1h','live','finished'])
- `send_notification(guild_id, channel_id, notification_type, match_summary)` -> bool

---

## 10. Testes e qualidade

- Testes unitários:
  - Parser de payloads da PandaScore
  - Funções de decisão (should_notify)
  - DB: inserção/checagem em `notifications_sent`
- Testes de integração (ambiente local):
  - Rodar o bot em servidor de teste e simular payloads

Ferramentas sugeridas:
- pytest, pytest-asyncio
- flake8 / ruff para lint

---

## 11. Deploy e operações

- Recomendado: Railway / Render / Fly.io
- Persistência: montar volume para `data/bot.db`
- Variáveis de ambiente obrigatórias: `DISCORD_TOKEN`, `PANDASCORE_API_KEY`, `DATABASE_PATH`
- Health check: endpoint HTTP simples (opcional) que verifique conexão com DB e estado do scheduler

---

## 12. Observações finais

- Manter o design simples: foco em confiabilidade e evitar notificações duplicadas.
- Documentar comandos e fluxos em `docs/` para usuário final.
- Próximo passo: implementar client PandaScore e job de polling, validar com um servidor de teste.

---

Document prepared by project automation — revisão manual recomendada.
    # --- Favorite Teams ---
    async def add_favorite_team(self, guild_id: str, team_slug: str, team_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO favorite_teams (guild_id, team_slug, team_name) VALUES (?, ?, ?)",
                (guild_id, team_slug, team_name)
            )
            await db.commit()
    
    async def remove_favorite_team(self, guild_id: str, team_slug: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM favorite_teams WHERE guild_id = ? AND team_slug = ?",
                (guild_id, team_slug)
            )
            await db.commit()
    
    async def get_favorite_teams(self, guild_id: str) -> List[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM favorite_teams WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    # --- Notifications ---
    async def was_notification_sent(self, match_id: int, guild_id: str, notification_type: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM notifications_sent WHERE match_id = ? AND guild_id = ? AND notification_type = ?",
                (match_id, guild_id, notification_type)
            ) as cursor:
                return await cursor.fetchone() is not None
    
    async def mark_notification_sent(self, match_id: int, guild_id: str, notification_type: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO notifications_sent (match_id, guild_id, notification_type) VALUES (?, ?, ?)",
                (match_id, guild_id, notification_type)
            )
            await db.commit()
    
    # --- Match Cache ---
    async def cache_match(self, match_id: int, data: dict, status: str, scheduled_at: datetime):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO matches_cache 
                   (match_id, data, status, scheduled_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (match_id, json.dumps(data), status, scheduled_at, datetime.now())
            )
            await db.commit()
    
    async def get_cached_match(self, match_id: int) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM matches_cache WHERE match_id = ?", (match_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    result = dict(row)
                    result['data'] = json.loads(result['data'])
                    return result
                return None
```

---

## 🔔 4. Sistema de Notificações

### 4.1. Tipos de Notificação

```python
# src/models/notification.py
from enum import Enum

class NotificationType(Enum):
    TWENTY_FOUR_HOURS = "24h"
    ONE_HOUR = "1h"
    LIVE = "live"
    FINISHED = "finished"

# Janelas de tempo para cada tipo
NOTIFICATION_WINDOWS = {
    NotificationType.TWENTY_FOUR_HOURS: (23 * 60, 25 * 60),  # 23h-25h em minutos
    NotificationType.ONE_HOUR: (50, 70),  # 50min-70min
}
```

### 4.2. Lógica de Envio

```python
# src/services/notification_service.py
from datetime import datetime, timedelta
from typing import List
import discord

class NotificationService:
    def __init__(self, bot, database, api_client):
        self.bot = bot
        self.db = database
        self.api = api_client
    
    async def check_and_send_notifications(self):
        """Verifica partidas e envia notificações"""
        # 1. Buscar partidas upcoming
        upcoming_matches = await self.api.get_upcoming_matches(game="csgo")
        
        # 2. Para cada partida, verificar se precisa notificar
        for match in upcoming_matches:
            await self._process_match_notifications(match)
        
        # 3. Verificar partidas ao vivo
        running_matches = await self.api.get_running_matches(game="csgo")
        for match in running_matches:
            await self._notify_live_match(match)
        
        # 4. Verificar partidas finalizadas (nas últimas 2h)
        past_matches = await self.api.get_past_matches(game="csgo", hours=2)
        for match in past_matches:
            await self._notify_finished_match(match)
    
    async def _process_match_notifications(self, match: dict):
        """Processa notificações de tempo (24h, 1h)"""
        match_time = datetime.fromisoformat(match['scheduled_at'].replace('Z', '+00:00'))
        now = datetime.now(match_time.tzinfo)
        
        time_until_match = (match_time - now).total_seconds() / 60  # em minutos
        
        # Verificar 24h
        if 23 * 60 <= time_until_match <= 25 * 60:
            await self._send_time_notification(match, NotificationType.TWENTY_FOUR_HOURS)
        
        # Verificar 1h
        elif 50 <= time_until_match <= 70:
            await self._send_time_notification(match, NotificationType.ONE_HOUR)
    
    async def _send_time_notification(self, match: dict, notification_type: NotificationType):
        """Envia notificação de tempo para todos os servidores"""
        # Buscar todos os servidores configurados
        guilds = await self.db.get_all_guilds()
        
        for guild_data in guilds:
            guild_id = guild_data['guild_id']
            
            # Verificar se já foi enviada
            if await self.db.was_notification_sent(match['id'], guild_id, notification_type.value):
                continue
            
            # Verificar filtros de time favorito
            if not await self._should_notify_guild(guild_id, match):
                continue
            
            # Enviar notificação
            channel = self.bot.get_channel(int(guild_data['notification_channel_id']))
            if channel:
                embed = create_time_notification_embed(match, notification_type)
                await channel.send(embed=embed)
                await self.db.mark_notification_sent(match['id'], guild_id, notification_type.value)
    
    async def _should_notify_guild(self, guild_id: str, match: dict) -> bool:
        """Verifica se deve notificar o servidor (filtros)"""
        favorite_teams = await self.db.get_favorite_teams(guild_id)
        
        # Se não tem favoritos, notifica todas
        if not favorite_teams:
            return True
        
        # Se tem favoritos, verifica se algum time está na partida
        favorite_slugs = {team['team_slug'] for team in favorite_teams}
        match_team_slugs = {opp['opponent']['slug'] for opp in match['opponents']}
        
        return bool(favorite_slugs & match_team_slugs)
```

### 4.3. Templates de Embeds

```python
# src/utils/embeds.py
import discord
from datetime import datetime
from src.models.notification import NotificationType

def create_time_notification_embed(match: dict, notification_type: NotificationType) -> discord.Embed:
    """Cria embed para notificações de tempo (24h, 1h)"""
    
    # Cores por tipo
    colors = {
        NotificationType.TWENTY_FOUR_HOURS: 0x3498db,  # Azul
        NotificationType.ONE_HOUR: 0xf39c12,  # Laranja
    }
    
    # Títulos
    titles = {
        NotificationType.TWENTY_FOUR_HOURS: "⏰ Partida em 24 horas!",
        NotificationType.ONE_HOUR: "⚠️ Partida em 1 hora!",
    }
    
    team1 = match['opponents'][0]['opponent']
    team2 = match['opponents'][1]['opponent']
    
    embed = discord.Embed(
        title=titles[notification_type],
        description=f"**{team1['name']}** vs **{team2['name']}**",
        color=colors[notification_type],
        timestamp=datetime.now()
    )
    
    # Adicionar campos
    embed.add_field(
        name="🏆 Torneio",
        value=match['tournament']['name'],
        inline=False
    )
    
    scheduled_time = datetime.fromisoformat(match['scheduled_at'].replace('Z', '+00:00'))
    embed.add_field(
        name="⏰ Horário",
        value=f"<t:{int(scheduled_time.timestamp())}:F>",
        inline=True
    )
    
    bo_type = f"BO{match['number_of_games']}"
    embed.add_field(
        name="📺 Formato",
        value=bo_type,
        inline=True
    )
    
    # Logos dos times
    if team1.get('image_url'):
        embed.set_thumbnail(url=team1['image_url'])
    
    embed.set_footer(text="Dados: PandaScore API")
    
    return embed

def create_live_notification_embed(match: dict) -> discord.Embed:
    """Cria embed para partida ao vivo"""
    team1 = match['opponents'][0]['opponent']
    team2 = match['opponents'][1]['opponent']
    
    embed = discord.Embed(
        title="🔴 PARTIDA AO VIVO!",
        description=f"**{team1['name']}** vs **{team2['name']}**",
        color=0xe74c3c,  # Vermelho
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🏆 Torneio",
        value=match['tournament']['name'],
        inline=False
    )
    
    embed.add_field(
        name="📊 Status",
        value="Em andamento",
        inline=True
    )
    
    bo_type = f"BO{match['number_of_games']}"
    embed.add_field(
        name="📺 Formato",
        value=bo_type,
        inline=True
    )
    
    if match.get('official_stream_url'):
        embed.add_field(
            name="🎥 Stream",
            value=f"[Assistir]({match['official_stream_url']})",
            inline=False
        )
    
    if team1.get('image_url'):
        embed.set_thumbnail(url=team1['image_url'])
    
    embed.set_footer(text="Dados: PandaScore API")
    
    return embed

def create_finished_notification_embed(match: dict) -> discord.Embed:
    """Cria embed para partida finalizada"""
    team1 = match['opponents'][0]['opponent']
    team2 = match['opponents'][1]['opponent']
    
    # Determinar vencedor
    winner = match.get('winner')
    winner_name = winner['name'] if winner else "Empate"
    
    results = match.get('results', [])
    score1 = results[0]['score'] if len(results) > 0 else 0
    score2 = results[1]['score'] if len(results) > 1 else 0
    
    embed = discord.Embed(
        title="✅ Partida Finalizada",
        description=f"**{team1['name']}** {score1} - {score2} **{team2['name']}**",
        color=0x2ecc71,  # Verde
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🏆 Torneio",
        value=match['tournament']['name'],
        inline=False
    )
    
    embed.add_field(
        name="🎖️ Vencedor",
        value=winner_name,
        inline=True
    )
    
    embed.add_field(
        name="📊 Placar",
        value=f"{score1} - {score2}",
        inline=True
    )
    
    if team1.get('image_url'):
        embed.set_thumbnail(url=team1['image_url'])
    
    embed.set_footer(text="Dados: PandaScore API")
    
    return embed
```

---

## ⏱️ 5. Sistema de Agendamento (APScheduler)

### 5.1. Configuração do Scheduler

```python
# src/services/scheduler_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, notification_service):
        self.scheduler = AsyncIOScheduler()
        self.notification_service = notification_service
    
    def start(self):
        """Inicia os jobs de polling"""
        # Job principal: checar partidas a cada 15 minutos
        self.scheduler.add_job(
            self.notification_service.check_and_send_notifications,
            trigger=IntervalTrigger(minutes=15),
            id='check_matches',
            name='Check matches and send notifications',
            replace_existing=True
        )
        
        # Job de limpeza: limpar cache antigo a cada 24h
        self.scheduler.add_job(
            self._cleanup_old_cache,
            trigger=IntervalTrigger(hours=24),
            id='cleanup_cache',
            name='Cleanup old cache',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler iniciado com sucesso")
    
    async def _cleanup_old_cache(self):
        """Remove partidas antigas do cache (>7 dias)"""
        # Implementar limpeza do banco
        pass
    
    def stop(self):
        """Para o scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler parado")
```

### 5.2. Intervalos de Polling

```python
# Configurações em config/settings.py
POLLING_INTERVALS = {
    "standard": 15,  # minutos - checagem padrão
    "live": 5,       # minutos - partidas ao vivo (futuro)
    "cleanup": 24 * 60  # minutos - limpeza de cache
}
```

---

## 🎮 6. Comandos do Discord (Cogs)

### 6.1. Estrutura de Cogs

```python
# src/cogs/config.py
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.database
    
    @slash_command(
        name="setup",
        description="Configurar canal de notificações"
    )
    @commands.has_permissions(administrator=True)
    async def setup(
        self,
        ctx: discord.ApplicationContext,
        canal: Option(discord.TextChannel, "Canal para enviar notificações", required=True)
    ):
        """Configura o canal de notificações do servidor"""
        await self.db.add_guild(str(ctx.guild_id), str(canal.id))
        
        embed = discord.Embed(
            title="✅ Configuração Concluída",
            description=f"As notificações serão enviadas em {canal.mention}",
            color=0x2ecc71
        )
        embed.add_field(
            name="📌 Próximos Passos",
            value="Use `/seguir [time]` para adicionar times favoritos\nOu deixe em branco para receber todas as partidas",
            inline=False
        )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @slash_command(
        name="idioma",
        description="Alterar idioma das notificações"
    )
    @commands.has_permissions(administrator=True)
    async def idioma(
        self,
        ctx: discord.ApplicationContext,
        idioma: Option(str, "Idioma desejado", choices=["pt-BR", "en"], required=True)
    ):
        """Altera o idioma das notificações"""
        # Implementar mudança de idioma no banco
        await ctx.respond(f"✅ Idioma alterado para {idioma}", ephemeral=True)

def setup(bot):
    bot.add_cog(ConfigCog(bot))
```

```python
# src/cogs/teams.py
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

class TeamsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.database
    
    @slash_command(
        name="seguir",
        description="Adicionar time aos favoritos"
    )
    async def seguir(
        self,
        ctx: discord.ApplicationContext,
        time: Option(str, "Nome do time (ex: FURIA, NAVI)", required=True)
    ):
        """Adiciona um time à lista de favoritos"""
        # Normalizar nome do time (lowercase, slug)
        team_slug = time.lower().replace(" ", "-")
        
        await self.db.add_favorite_team(str(ctx.guild_id), team_slug, time)
        
        embed = discord.Embed(
            title="✅ Time Adicionado",
            description=f"Agora você receberá notificações de **{time}**",
            color=0x2ecc71
        )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="desseguir",
        description="Remover time dos favoritos"
    )
    async def desseguir(
        self,
        ctx: discord.ApplicationContext,
        time: Option(str, "Nome do time", required=True)
    ):
        """Remove um time da lista de favoritos"""
        team_slug = time.lower().replace(" ", "-")
        
        await self.db.remove_favorite_team(str(ctx.guild_id), team_slug)
        
        embed = discord.Embed(
            title="✅ Time Removido",
            description=f"Você não receberá mais notificações de **{time}**",
            color=0x3498db
        )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="meustimes",
        description="Listar times favoritos"
    )
    async def meustimes(self, ctx: discord.ApplicationContext):
        """Lista todos os times favoritos do servidor"""
        teams = await self.db.get_favorite_teams(str(ctx.guild_id))
        
        if not teams:
            embed = discord.Embed(
                title="📋 Times Favoritos",
                description="Nenhum time configurado. Use `/seguir [time]` para adicionar.",
                color=0x95a5a6
            )
        else:
            teams_list = "\n".join([f"• {team['team_name']}" for team in teams])
            embed = discord.Embed(
                title="📋 Times Favoritos",
                description=teams_list,
                color=0x3498db
            )
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(TeamsCog(bot))
```

```python
# src/cogs/matches.py
import discord
from discord.ext import commands
from discord.commands import slash_command
from datetime import datetime, timedelta

class MatchesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = bot.api_client
    
    @slash_command(
        name="partidas",
        description="Listar próximas partidas de CS2"
    )
    async def partidas(self, ctx: discord.ApplicationContext):
        """Lista partidas dos próximos 2 dias"""
        await ctx.defer()
        
        matches = await self.api.get_upcoming_matches(game="csgo", limit=10)
        
        if not matches:
            await ctx.respond("Nenhuma partida próxima encontrada.")
            return
        
        embed = discord.Embed(
            title="📅 Próximas Partidas de CS2",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        for match in matches[:5]:  # Limitar a 5 para não ficar muito grande
            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            tournament = match['tournament']['name']
            scheduled = datetime.fromisoformat(match['scheduled_at'].replace('Z', '+00:00'))
            
            embed.add_field(
                name=f"{team1} vs {team2}",
                value=f"🏆 {tournament}\n⏰ <t:{int(scheduled.timestamp())}:R>",
                inline=False
            )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="aovivo",
        description="Ver partidas acontecendo agora"
    )
    async def aovivo(self, ctx: discord.ApplicationContext):
        """Lista partidas ao vivo"""
        await ctx.defer()
        
        matches = await self.api.get_running_matches(game="csgo")
        
        if not matches:
            await ctx.respond("Nenhuma partida ao vivo no momento.")
            return
        
        embed = discord.Embed(
            title="🔴 Partidas Ao Vivo",
            color=0xe74c3c,
            timestamp=datetime.now()
        )
        
        for match in matches:
            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            tournament = match['tournament']['name']
            
            embed.add_field(
                name=f"{team1} vs {team2}",
                value=f"🏆 {tournament}\n📊 Em andamento",
                inline=False
            )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="resultados",
        description="Ver resultados recentes"
    )
    async def resultados(self, ctx: discord.ApplicationContext):
        """Lista resultados das últimas 24h"""
        await ctx.defer()
        
        matches = await self.api.get_past_matches(game="csgo", hours=24, limit=5)
        
        if not matches:
            await ctx.respond("Nenhum resultado recente encontrado.")
            return
        
        embed = discord.Embed(
            title="✅ Resultados Recentes",
            color=0x2ecc71,
            timestamp=datetime.now()
        )
        
        for match in matches:
            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            tournament = match['tournament']['name']
            
            results = match.get('results', [])
            score1 = results[0]['score'] if len(results) > 0 else 0
            score2 = results[1]['score'] if len(results) > 1 else 0
            
            winner = match.get('winner', {}).get('name', 'N/A')
            
            embed.add_field(
                name=f"{team1} {score1} - {score2} {team2}",
                value=f"🏆 {tournament}\n🎖️ Vencedor: {winner}",
                inline=False
            )
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(MatchesCog(bot))
```

---

## 🔌 7. Cliente da API (PandaScore)

```python
# src/services/pandascore_service.py
import aiohttp
import os
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PandaScoreClient:
    def __init__(self):
        self.base_url = "https://api.pandascore.co"
        self.api_token = os.getenv("PANDASCORE_API_KEY")
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna sessão aiohttp (singleton)"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Accept": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _request(self, endpoint: str, params: dict = None) -> dict:
        """Faz requisição à API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Erro na requisição à API: {e}")
            return []
    
    async def get_upcoming_matches(self, game: str = "csgo", limit: int = 50) -> List[dict]:
        """Busca partidas futuras"""
        params = {
            "filter[status]": "not_started",
            "sort": "scheduled_at",
            "per_page": limit
        }
        matches = await self._request(f"/{game}/matches/upcoming", params)
        return matches
    
    async def get_running_matches(self, game: str = "csgo") -> List[dict]:
        """Busca partidas ao vivo"""
        params = {
            "filter[status]": "running"
        }
        matches = await self._request(f"/{game}/matches/running", params)
        return matches
    
    async def get_past_matches(self, game: str = "csgo", hours: int = 24, limit: int = 20) -> List[dict]:
        """Busca partidas finalizadas nas últimas X horas"""
        now = datetime.utcnow()
        since = now - timedelta(hours=hours)
        
        params = {
            "filter[status]": "finished",
            "filter[end_at]": f">{since.isoformat()}Z",
            "sort": "-end_at",
            "per_page": limit
        }
        matches = await self._request(f"/{game}/matches/past", params)
        return matches
    
    async def get_match_details(self, game: str = "csgo", match_id: int = None) -> Optional[dict]:
        """Busca detalhes de uma partida específica"""
        match = await self._request(f"/{game}/matches/{match_id}")
        return match
    
    async def close(self):
        """Fecha a sessão"""
        if self.session and not self.session.closed:
            await self.session.close()
```

---

## 🤖 8. Bot Principal

```python
# src/bot.py
import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

from src.database.db import Database
from src.services.pandascore_service import PandaScoreClient
from src.services.notification_service import NotificationService
from src.services.scheduler_service import SchedulerService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True

# Criar bot
bot = commands.Bot(
    command_prefix="!",  # Prefix para comandos de texto (opcional)
    intents=intents,
    description="Bot de notificações de partidas de CS2"
)

# Inicializar serviços
bot.database = Database()
bot.api_client = PandaScoreClient()

@bot.event
async def on_ready():
    """Evento quando bot está pronto"""
    logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    logger.info(f"Conectado a {len(bot.guilds)} servidores")
    
    # Conectar ao banco de dados
    await bot.database.connect()
    logger.info("Banco de dados conectado")
    
    # Inicializar sistema de notificações
    notification_service = NotificationService(bot, bot.database, bot.api_client)
    
    # Iniciar scheduler
    scheduler = SchedulerService(notification_service)
    scheduler.start()
    logger.info("Sistema de notificações iniciado")
    
    # Registrar comandos slash
    await bot.sync_commands()
    logger.info("Comandos slash registrados")

@bot.event
async def on_guild_join(guild):
    """Evento quando bot entra em um servidor"""
    logger.info(f"Bot adicionado ao servidor: {guild.name} (ID: {guild.id})")
    
    # Enviar mensagem de boas-vindas no primeiro canal disponível
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="👋 Olá! Obrigado por me adicionar!",
                description="Sou um bot de notificações de partidas de CS2.",
                color=0x3498db
            )
            embed.add_field(
                name="🚀 Como começar",
                value="Use o comando `/setup` para configurar o canal de notificações.",
                inline=False
            )
            embed.add_field(
                name="📚 Ajuda",
                value="Use `/ajuda` para ver todos os comandos disponíveis.",
                inline=False
            )
            await channel.send(embed=embed)
            break

@bot.event
async def on_guild_remove(guild):
    """Evento quando bot sai de um servidor"""
    logger.info(f"Bot removido do servidor: {guild.name} (ID: {guild.id})")
    # Limpar dados do servidor do banco (opcional)

# Carregar cogs
bot.load_extension("src.cogs.config")
bot.load_extension("src.cogs.teams")
bot.load_extension("src.cogs.matches")
bot.load_extension("src.cogs.help")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN não encontrado no .env")
        exit(1)
    
    bot.run(token)
```

---

## 📦 9. Dependências (requirements.txt)

```txt
# Discord
py-cord>=2.4.0

# HTTP Client
aiohttp>=3.9.0

# Database
aiosqlite>=0.19.0

# Scheduler
APScheduler>=3.10.0

# Environment Variables
python-dotenv>=1.0.0

# Utilities
python-dateutil>=2.8.2
```

---

## ⚙️ 10. Configurações (.env)

```bash
# .env.example

# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# PandaScore API Key
PANDASCORE_API_KEY=your_pandascore_api_key_here

# Database Path (opcional)
DATABASE_PATH=data/bot.db

# Polling Intervals (em minutos)
POLLING_STANDARD=15
POLLING_LIVE=5

# Logging Level
LOG_LEVEL=INFO
```

---

## 🚀 11. Deploy

### 11.1. Railway

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python -m src.bot"
restartPolicyType = "always"
```

### 11.2. Render

```yaml
# render.yaml
services:
  - type: web
    name: bot-hltv
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python -m src.bot"
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: PANDASCORE_API_KEY
        sync: false
```

---

## 📊 12. Métricas e Monitoramento

### 12.1. Logs

```python
# Sistema de logging estruturado
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo (com rotação)
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

### 12.2. Métricas de Sucesso

- ✅ **Uptime**: > 99% mensal
- ✅ **Latência de Notificações**: < 5 minutos do evento
- ✅ **Taxa de Erro**: < 1% das requisições
- ✅ **Notificações Duplicadas**: 0
- ✅ **Tempo de Resposta de Comandos**: < 2 segundos
- ✅ **Consumo de Memória**: < 512MB

---

## 🔐 13. Segurança

### 13.1. Boas Práticas

- ✅ Nunca commitar `.env` (incluir em `.gitignore`)
- ✅ Tokens em variáveis de ambiente
- ✅ Validação de inputs de usuários
- ✅ Rate limiting em comandos
- ✅ Logs sem informações sensíveis
- ✅ Permissões mínimas necessárias

### 13.2. Conformidade Discord

- ✅ Respeitar rate limits da API do Discord
- ✅ Não armazenar mensagens de usuários
- ✅ Conformidade com ToS do Discord
- ✅ Política de privacidade clara

---

## 📝 14. Notas Finais

### 14.1. Limitações do MVP

- ❌ Sem suporte a webhooks (PandaScore gratuito não oferece)
- ❌ Sem notificações via DM (implementar no futuro)
- ❌ Sem filtros avançados de tier/evento (v2.0)
- ❌ Sem dashboard web (v2.0)

### 14.2. Roadmap Futuro

**v1.1:**
- Sistema de logs avançado
- Testes unitários e de integração
- Otimizações de performance

**v2.0:**
- Migração para PostgreSQL/Turso
- Dashboard web
- Suporte multi-idioma completo
- Estatísticas e análises
- Filtros avançados

---

**Versão do Documento**: 2.0 (Python/Pycord)  
**Última Atualização**: 15 de novembro de 2025  
**Autor**: Projeto Bot HLTV
