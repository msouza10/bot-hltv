"""
Serviço para buscar streams de jogos na Twitch.

Usamos isso quando a API PandaScore não retorna raw_url (raro),
para encontrar automaticamente streams do jogo sendo transmitido.
"""

import aiohttp
import os
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TwitchSearchService:
    """Busca streams na Twitch de forma automatizada."""
    
    # Cache para evitar múltiplas buscas da mesma query em curto prazo
    _search_cache: Dict[str, tuple] = {}  # {query: (result, timestamp)}
    CACHE_DURATION = 300  # 5 minutos
    
    def __init__(self):
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None
    
    async def _get_access_token(self) -> Optional[str]:
        """
        Obtém token de acesso OAuth da Twitch.
        O token é cacheado por 1 hora (válido por 1 hora na API Twitch).
        """
        # Verificar se token ainda é válido
        if self.access_token and self.token_expires_at > datetime.utcnow():
            return self.access_token
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://id.twitch.tv/oauth2/token"
                params = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                }
                
                async with session.post(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Erro ao obter token Twitch: {response.status}")
                        return None
                    
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                    
                    logger.debug(f"✅ Token Twitch obtido, válido por {expires_in}s")
                    return self.access_token
        
        except Exception as e:
            logger.error(f"❌ Erro ao obter token Twitch: {e}")
            return None
    
    async def search_streams(
        self,
        championship: str,
        team1_name: str,
        team2_name: str,
        language: str = "pt"
    ) -> Optional[Dict]:
        """
        Busca streams na Twitch para uma partida específica.
        
        Estratégia de busca (em ordem de prioridade):
        1. Procura por "championship team1 team2"
        2. Procura por "team1 vs team2"
        3. Procura apenas pelo "championship"
        4. Procura por "Counter-Strike 2" ou "CS2" (fallback por game)
        
        Args:
            championship: Nome do campeonato (ex: "ESL Pro League")
            team1_name: Nome do time 1
            team2_name: Nome do time 2
            language: Idioma preferido dos streams (fallback: "en" se não achar)
        
        Returns:
            Dict com dados do stream ou None se não encontrado
            {
                "channel_name": "nome_do_canal",
                "url": "https://twitch.tv/nome_do_canal",
                "viewer_count": 1234,
                "title": "ESL Pro League - Team1 vs Team2",
                "is_automated": true,
                "language": "pt" ou "en"
            }
        """
        
        # Construir queries em ordem de prioridade
        queries = [
            f"{championship} {team1_name} {team2_name}",
            f"{team1_name} vs {team2_name}",
            f"{championship} live",
            championship,
            "Counter-Strike 2",  # Fallback: procurar por CS2
            "CS2"
        ]
        
        token = await self._get_access_token()
        if not token:
            logger.warning("❌ Não conseguiu obter token Twitch para busca de streams")
            return None
        
        try:
            # ESTRATÉGIA: Usar game_id é mais confiável que busca textual
            # Counter-Strike (genérico) = game_id 32399
            # Vamos primeiro tentar busca por categoria + scoring no código
            
            logger.debug(f"🎮 Buscando streams de Counter-Strike (game_id=32399)...")
            
            result = await self._search_twitch_api(
                token=token,
                query="counter-strike 2",  # Fallback descritivo
                language=language,
                championship=championship,
                team1=team1_name,
                team2=team2_name,
                game_id="32399"  # Counter-Strike genérico inclui CS2
            )
            
            if result:
                logger.info(f"✅ Stream encontrado: {result['channel_name']} ({result['viewer_count']} viewers)")
                return result
            
            logger.warning(f"⚠️ Nenhum stream encontrado para: {championship} - {team1_name} vs {team2_name}")
            return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar streams na Twitch: {e}")
            return None
    
    async def _search_twitch_api(
        self,
        token: str,
        query: str,
        language: str,
        championship: str = "",
        team1: str = "",
        team2: str = "",
        game_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Realiza a busca na API Twitch.
        
        Se game_id for fornecido, usa busca estruturada por categoria (MELHOR).
        Senão, usa busca textual por query (MENOS CONFIÁVEL - latência de indexação).
        """
        logger.debug(f"🔍 Consulta à API Twitch: '{query}'" + (f" (game_id={game_id})" if game_id else ""))
        
        url = "https://api.twitch.tv/helix/streams"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        # Estratégia: preferir filtros estruturados
        if game_id:
            # MELHOR: Busca estruturada por categoria
            # IMPORTANTE: Removemos language filter para não excluir streams em outros idiomas
            # Exemplo: "Betera vs Leo" estava em RU, mas não aparecia com language=pt
            params = {
                "game_id": game_id,
                "first": 100,  # Aumentado para 100 para mais opções
            }
        else:
            # FALLBACK: Busca textual (tem latência de indexação)
            # NOTE: Este endpoint /streams não suporta 'query' para texto livre
            # Estamos usando como fallback, mas pode não funcionar bem
            params = {
                "first": 100,  # Aumentado para 100 para mais opções
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logger.error(f"❌ Erro ao buscar streams: {response.status}")
                        return None
                    
                    data = await response.json()
                    streams = data.get("data", [])
                    
                    if not streams:
                        logger.debug(f"❌ Nenhuma stream retornada pela API")
                        return None
                    
                    # Encontrar o melhor match usando scoring
                    best_match = self._find_best_match(
                        streams=streams,
                        query=query,
                        language=language,
                        championship=championship,
                        team1=team1,
                        team2=team2
                    )
                    return best_match
        
        except Exception as e:
            logger.error(f"❌ Erro ao consultar API Twitch: {e}")
            return None
    
    def _find_best_match(
        self,
        streams: List[Dict],
        query: str,
        language: str,
        championship: str = "",
        team1: str = "",
        team2: str = ""
    ) -> Optional[Dict]:
        """
        Encontra o melhor match entre os streams retornados.
        
        CRITÉRIO OBRIGATÓRIO (Prerequisito):
        - Título DEVE ter uma pontuação mínima de relevância
        
        Sistema de Pontuação por Palavras:
        - Cada palavra é quebrada e comparada individualmente
        - Exemplo: "Dust2.dk Ligaen" = ["dust2", "dk", "ligaen"]
        - Busca em "POWER Ligaen" encontra: "ligaen" (+10 pts)
        - Busca por time "Prestige" em "Prestige vs..." = +20 pts
        
        Score Mínimo Requerido: 15 pts (para aceitar stream)
        
        Pontuação:
        - Cada palavra do campeonato: +10 pts
        - Cada time encontrado: +20 pts
        - Viewers: até +100 pts
        - Idioma correto: +50 pts
        """
        
        query_lower = query.lower()
        championship_lower = championship.lower().strip()
        team1_lower = team1.lower().strip()
        team2_lower = team2.lower().strip()
        
        matching_streams = []
        MIN_SCORE = 10  # Score mínimo para aceitar stream (reduzido para ser mais flexível)
        FALLBACK_MIN_SCORE = 10  # Score mais baixo para fallback (quando nada encontrado)
        
        logger.debug(f"🔍 Filtrando streams com scoring: championship='{championship}', team1='{team1}', team2='{team2}'")
        logger.debug(f"   Score mínimo requerido: {MIN_SCORE} pts")
        
        # Função para quebrar e extrair palavras-chave
        def extract_keywords(text: str) -> List[str]:
            """Extrai palavras-chave de um texto."""
            if not text:
                return []
            
            # Converter para minúsculas e remover pontuação
            text = text.lower()
            words = text.split()
            
            keywords = []
            for word in words:
                # Remover pontuação
                clean_word = word.strip('.,;:!?)[]"\'|')
                if clean_word:
                    keywords.append(clean_word)
                    
                    # Se tem ponto, também adicionar a parte antes do ponto
                    if "." in clean_word:
                        base = clean_word.split(".")[0].strip()
                        if base:
                            keywords.append(base)
            
            return keywords
        
        # Função para calcular score de relevância
        def calculate_relevance_score(title: str, championship: str, team1: str, team2: str) -> int:
            """
            Calcula score de relevância do título.
            Retorna score baseado em palavras encontradas.
            
            BONUS SPECIAL: Se encontra AMBOS os times + campeonato = +200 pontos!
            Isso garante que matches reais (ex: "Betera vs Leo | CCT Europe")
            sejam favorecidos sobre false positives (ex: "leo_drinks is back!")
            """
            score = 0
            title_keywords = extract_keywords(title)
            title_lower = title.lower()
            
            championship_found = False
            team1_found = False
            team2_found = False
            
            # Score por campeonato (cada palavra do campeonato)
            if championship:
                champ_keywords = extract_keywords(championship)
                for champ_word in champ_keywords:
                    if champ_word in title_keywords:
                        logger.debug(f"      ✓ Campeonato: encontrou '{champ_word}' em '{title[:50]}...' +10 pts")
                        score += 10
                        championship_found = True
                    elif champ_word in title_lower:
                        # Partial match (substring)
                        logger.debug(f"      ✓ Campeonato: encontrou parcial '{champ_word}' +5 pts")
                        score += 5
                        championship_found = True
            
            # Score por time 1 (cada palavra do time)
            if team1:
                team1_keywords = extract_keywords(team1)
                for team1_word in team1_keywords:
                    if team1_word in title_keywords:
                        logger.debug(f"      ✓ Time 1: encontrou '{team1_word}' +20 pts")
                        score += 20
                        team1_found = True
                    elif team1_word in title_lower and len(team1_word) > 3:
                        # Partial match (substring) mas só se > 3 caracteres
                        logger.debug(f"      ✓ Time 1: encontrou parcial '{team1_word}' +10 pts")
                        score += 10
                        team1_found = True
            
            # Score por time 2 (cada palavra do time)
            if team2:
                team2_keywords = extract_keywords(team2)
                for team2_word in team2_keywords:
                    if team2_word in title_keywords:
                        logger.debug(f"      ✓ Time 2: encontrou '{team2_word}' +20 pts")
                        score += 20
                        team2_found = True
                    elif team2_word in title_lower and len(team2_word) > 3:
                        # Partial match (substring) mas só se > 3 caracteres
                        logger.debug(f"      ✓ Time 2: encontrou parcial '{team2_word}' +10 pts")
                        score += 10
                        team2_found = True
            
            # BONUS ESPECIAL: Encontrou ambos os times AND campeonato
            if team1_found and team2_found and championship_found:
                bonus = 200
                logger.debug(f"      🎁 BONUS ESPECIAL: Ambos times + campeonato encontrados! +{bonus} pts")
                score += bonus
            
            return score
        
        # Filtrar streams que correspondam à query
        for stream in streams:
            title = stream.get("title", "")
            
            # Calcular score de relevância
            relevance_score = calculate_relevance_score(title, championship_lower, team1_lower, team2_lower)
            
            # Definir score mínimo dinâmico:
            # - Se tem campeonato OU times: requer MIN_SCORE (rigoroso)
            # - Se NÃO tem campeonato E NÃO tem times: aceita qualquer stream de CS2 (fallback relaxado)
            min_score_required = MIN_SCORE if (championship or team1 or team2) else 0
            
            # Se score abaixo do mínimo, pula
            if relevance_score < min_score_required:
                logger.debug(f"❌ Stream descartada: '{stream.get('user_login')}' - score {relevance_score} < {min_score_required}")
                continue
            
            # Pontuação total
            score = relevance_score
            
            # Bônus por viewers (mais viewers = melhor)
            viewer_count = stream.get("viewer_count", 0)
            viewer_bonus = min(viewer_count // 100, 100)  # Máx 100 pontos
            score += viewer_bonus
            if viewer_bonus > 0:
                logger.debug(f"   ✓ Viewers ({viewer_count}): +{viewer_bonus} ({stream.get('user_login')})")
            
            # Bônus por idioma correto
            if stream.get("language") == language:
                score += 50
                logger.debug(f"   ✓ Idioma correto: +50 ({stream.get('user_login')})")
            
            matching_streams.append({
                "stream": stream,
                "score": score
            })
            logger.debug(f"   ✅ Score final: {score} ({stream.get('user_login')})")
        
        if not matching_streams:
            logger.warning(f"⚠️ Nenhum stream encontrado com score mínimo ({MIN_SCORE})")
            logger.debug(f"   Tentando fallback com score mais baixo ({FALLBACK_MIN_SCORE})")
            return None
        
        # Se encontrou com score normal, usar normalmente
        # Se não, tentar com score mais baixo (já testado acima como fallback)
        
        # Retornar stream com maior score
        best_match = max(matching_streams, key=lambda x: x["score"])
        best = best_match["stream"]
        best_score = best_match["score"]
        
        logger.info(f"✅ Melhor match: {best.get('user_login')} (score: {best_score}, viewers: {best.get('viewer_count')})")
        
        return {
            "channel_name": best.get("user_login", "unknown"),
            "url": f"https://twitch.tv/{best.get('user_login', '')}",
            "viewer_count": best.get("viewer_count", 0),
            "title": best.get("title", ""),
            "is_automated": True,  # Flag importante!
            "language": best.get("language", "en")
        }


# Instância global (singleton)
_twitch_service: Optional[TwitchSearchService] = None


async def get_twitch_search_service() -> TwitchSearchService:
    """Obtém instância global do serviço Twitch."""
    global _twitch_service
    if _twitch_service is None:
        _twitch_service = TwitchSearchService()
    return _twitch_service
