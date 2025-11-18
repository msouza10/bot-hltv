"""
Serviço para integração com YouTube Data API v3.
Extrai informações do canal/streamer a partir do link.
"""

import aiohttp
import asyncio
import os
import logging
from typing import Optional, Dict
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class YouTubeService:
    """Serviço para buscar informações de canais/lives do YouTube via API v3."""
    
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ YOUTUBE_API_KEY não configurada no .env")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria a sessão HTTP."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Fecha a sessão HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    @staticmethod
    def _extract_channel_id_from_url(url: str) -> Optional[str]:
        """
        Extrai o identificador do canal/vídeo da URL do YouTube.
        
        Suporta:
        - youtube.com/watch?v=VIDEO_ID (vídeo)
        - youtu.be/VIDEO_ID (vídeo curto)
        - youtube.com/@CHANNEL_NAME (canal por handle)
        - youtube.com/c/CHANNEL_NAME (canal por nome)
        - youtube.com/channel/CHANNEL_ID (canal por ID)
        - youtube.com/@CHANNEL_NAME/live (live do canal)
        
        Args:
            url: URL do YouTube
            
        Returns:
            Video ID, channel ID, ou channel handle, ou None
        """
        try:
            # Remover protocolo e www
            url_clean = url.replace("https://", "").replace("http://", "").replace("www.", "")
            
            # Case 1: youtu.be/VIDEO_ID
            if url_clean.startswith("youtu.be/"):
                return url_clean.split("/")[1].split("?")[0]
            
            # Case 2: youtube.com/watch?v=VIDEO_ID
            if "youtube.com" in url_clean and "watch?v=" in url_clean:
                return url_clean.split("watch?v=")[1].split("&")[0]
            
            # Case 3: youtube.com/@CHANNEL_NAME ou youtube.com/@CHANNEL_NAME/live
            if "/@" in url_clean:
                parts = url_clean.split("/@")[1].split("/")
                return "@" + parts[0]  # Prefixar com @ para indicar que é handle
            
            # Case 4: youtube.com/c/CHANNEL_NAME
            if "/c/" in url_clean:
                parts = url_clean.split("/c/")[1].split("/")
                return "c:" + parts[0]  # Prefixar com c: para indicar custom URL
            
            # Case 5: youtube.com/channel/CHANNEL_ID
            if "/channel/" in url_clean:
                parts = url_clean.split("/channel/")[1].split("/")
                return "id:" + parts[0]  # Prefixar com id: para indicar channel ID
            
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair ID da URL YouTube: {url} - {e}")
            return None
    
    async def get_channel_name(self, url: str) -> Optional[str]:
        """
        Obtém o nome do canal/streamer a partir de uma URL do YouTube.
        
        Para URLs de vídeo e live, tenta usar a API.
        Para URLs de canal, usa o fallback de extração da URL.
        
        Args:
            url: URL do YouTube
            
        Returns:
            Nome do canal/streamer ou None
        """
        if not self.api_key:
            logger.debug(f"⚠️ YouTube API Key não configurada, usando fallback para URL: {url}")
            return await self._extract_channel_name_fallback(url)
        
        try:
            identifier = self._extract_channel_id_from_url(url)
            if not identifier:
                logger.warning(f"❌ Não consegui extrair ID da URL: {url}")
                return await self._extract_channel_name_fallback(url)
            
            session = await self._get_session()
            
            # Se é um vídeo (sem prefixo ou é youtu.be), buscar o canal do vídeo
            # Este é o caso mais comum e mais confiável
            if not identifier.startswith(("@", "c:", "id:")):
                channel_name = await self._get_channel_from_video(session, identifier)
                if channel_name:
                    return channel_name
                else:
                    # Fallback se falhar
                    return await self._extract_channel_name_fallback(url)
            
            # Para outros tipos, usar fallback (mais confiável que a API)
            return await self._extract_channel_name_fallback(url)
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar nome do canal YouTube ({url}): {e}")
            return await self._extract_channel_name_fallback(url)
    
    async def _get_channel_from_video(self, session: aiohttp.ClientSession, video_id: str) -> Optional[str]:
        """Busca o nome do canal a partir do ID de um vídeo."""
        try:
            params = {
                "part": "snippet",
                "id": video_id,
                "key": self.api_key
            }
            
            async with session.get(f"{self.base_url}/videos", params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("items"):
                        channel_title = data["items"][0].get("snippet", {}).get("channelTitle")
                        if channel_title:
                            logger.debug(f"✅ Nome do canal obtido via vídeo: {channel_title}")
                            return channel_title
                else:
                    logger.warning(f"⚠️ YouTube API retornou status {resp.status} para vídeo {video_id}")
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar vídeo {video_id}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar canal do vídeo {video_id}: {e}")
            return None
    
    async def _get_channel_by_handle(self, session: aiohttp.ClientSession, handle: str) -> Optional[str]:
        """Busca o nome do canal a partir do handle (@)."""
        try:
            params = {
                "part": "snippet",
                "forHandle": handle,
                "key": self.api_key
            }
            
            async with session.get(f"{self.base_url}/channels", params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("items"):
                        channel_title = data["items"][0].get("snippet", {}).get("title")
                        if channel_title:
                            logger.debug(f"✅ Nome do canal obtido via handle: {channel_title}")
                            return channel_title
                else:
                    logger.warning(f"⚠️ YouTube API retornou status {resp.status} para handle @{handle}")
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar handle @{handle}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar canal pelo handle @{handle}: {e}")
            return None
    
    async def _get_channel_by_custom_url(self, session: aiohttp.ClientSession, custom_url: str) -> Optional[str]:
        """Busca o nome do canal a partir da custom URL."""
        try:
            params = {
                "part": "snippet",
                "customUrl": custom_url,
                "key": self.api_key
            }
            
            async with session.get(f"{self.base_url}/channels", params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("items"):
                        channel_title = data["items"][0].get("snippet", {}).get("title")
                        if channel_title:
                            logger.debug(f"✅ Nome do canal obtido via custom URL: {channel_title}")
                            return channel_title
                else:
                    logger.warning(f"⚠️ YouTube API retornou status {resp.status} para custom URL {custom_url}")
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar custom URL {custom_url}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar canal pela custom URL {custom_url}: {e}")
            return None
    
    async def _get_channel_by_id(self, session: aiohttp.ClientSession, channel_id: str) -> Optional[str]:
        """Busca o nome do canal a partir do ID do canal."""
        try:
            params = {
                "part": "snippet",
                "id": channel_id,
                "key": self.api_key
            }
            
            async with session.get(f"{self.base_url}/channels", params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("items"):
                        channel_title = data["items"][0].get("snippet", {}).get("title")
                        if channel_title:
                            logger.debug(f"✅ Nome do canal obtido via ID: {channel_title}")
                            return channel_title
                else:
                    logger.warning(f"⚠️ YouTube API retornou status {resp.status} para channel ID {channel_id}")
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout ao buscar channel ID {channel_id}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar canal pelo ID {channel_id}: {e}")
            return None
    
    @staticmethod
    async def _extract_channel_name_fallback(url: str) -> Optional[str]:
        """
        Fallback quando a API não está disponível.
        Extrai o nome do canal direto da URL.
        
        Args:
            url: URL do YouTube
            
        Returns:
            Nome do canal extraído da URL, ou None
        """
        try:
            url_clean = url.replace("https://", "").replace("http://", "").replace("www.", "")
            
            # youtube.com/@CHANNEL_NAME
            if "/@" in url_clean:
                channel = url_clean.split("/@")[1].split("/")[0]
                return channel if channel else None
            
            # youtube.com/c/CHANNEL_NAME
            if "/c/" in url_clean:
                channel = url_clean.split("/c/")[1].split("/")[0]
                return channel if channel else None
            
            return None
        except Exception as e:
            logger.debug(f"Erro no fallback de extração de URL: {e}")
            return None


# Instância global
_youtube_service = None


def get_youtube_service() -> YouTubeService:
    """Obtém a instância global do serviço YouTube."""
    global _youtube_service
    if _youtube_service is None:
        _youtube_service = YouTubeService()
    return _youtube_service


async def close_youtube_service():
    """Fecha a sessão do serviço YouTube."""
    global _youtube_service
    if _youtube_service:
        await _youtube_service.close()
