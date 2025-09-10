import asyncio
import logging
from typing import Any
from telegram import Bot
from telegram.error import TimedOut, NetworkError, BadRequest
from telegram.request import HTTPXRequest

from .base import Channel
from core.settings import Settings
from telegram_helpers.chunker import Chunker
from telegram_helpers.markdown import escape_markdown_v2_preserving_code

log = logging.getLogger(__name__)

class TelegramChannel(Channel):
    """Канал для отправки сообщений в Telegram."""
    def __init__(self, timeout: float = 25.0):
        settings = Settings()
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in settings")

        self.bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            request=HTTPXRequest(read_timeout=timeout, connect_timeout=timeout),
        )
        self.chunker = Chunker(soft_limit=3900)
        self._lock = asyncio.Lock()

    async def send(self, destination: str, content: str, **kwargs: Any) -> None:
        if not content:
            log.warning("TelegramChannel: empty content, skipping send to %s", destination)
            return

        retries = 3
        delay = 1.0
        for attempt in range(retries):
            try:
                async with self._lock:
                    for chunk in self.chunker.split(content):
                        await self._deliver_chunk(destination, chunk, kwargs)
                log.info(f"Successfully sent message to {destination}")
                return
            except (TimedOut, NetworkError) as e:
                if attempt == retries - 1:
                    log.exception(f"Telegram send failed after {retries} retries")
                    raise
                log.warning(f"Telegram transient error: {e}, retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2

    async def _deliver_chunk(self, chat_id: str, chunk: str, kwargs: dict) -> None:
        """Пытается отправить один чанк, переключая режимы Markdown."""
        disable_preview = kwargs.get("disable_web_page_preview", True)
        try: # 1. Попытка с Markdown V1
            await self.bot.send_message(chat_id, chunk, parse_mode="Markdown", disable_web_page_preview=disable_preview)
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e): raise

        try: # 2. Попытка с Markdown V2
            v2_chunk = escape_markdown_v2_preserving_code(chunk)
            await self.bot.send_message(chat_id, v2_chunk, parse_mode="MarkdownV2", disable_web_page_preview=disable_preview)
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e): raise

        # 3. Отправка без форматирования как крайняя мера
        await self.bot.send_message(chat_id, chunk, disable_web_page_preview=disable_preview)