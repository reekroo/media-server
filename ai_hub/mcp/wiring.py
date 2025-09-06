from __future__ import annotations
from typing import Dict, Callable
from .tools import weather, sys_digest, media, news, gaming

def get_tools() -> Dict[str, Callable[..., str]]:
    """
    Регистрируем все доступные MCP-инструменты.
    Ключ — имя метода, значение — sync-функция (внутри сама вызывает asyncio.run при необходимости).
    """
    return {
        "weather.summary": weather.weather_summary,     # params: {payload: dict}
        "sys.digest":     sys_digest.system_digest,     # params: {config?: str}
        "media.digest":   media.media_digest,           # params: {config?: str}
        "news.digest":    news.news_digest,             # params: {config?: str, section?: str}
        "gaming.digest":  gaming.gaming_digest,         # params: {config?: str},
    }
