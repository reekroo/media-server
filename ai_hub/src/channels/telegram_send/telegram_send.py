from __future__ import annotations

import asyncio
import logging
from typing import Union

from telegram import Bot
from telegram.error import TimedOut, NetworkError
from telegram.request import HTTPXRequest

from ...core.context_mediator import send_markdown_safe_via_telegram

logger = logging.getLogger(__name__)

class TelegramClient:
    
    def __init__(self, token: str, *, timeout: float = 25.0) -> None:
        token = (token or "").strip()
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is empty")
        
        self.bot = Bot(
            token=token,
            request=HTTPXRequest(read_timeout=timeout, connect_timeout=timeout),
        )
        self._lock = asyncio.Lock()

    @staticmethod
    def _clean_chat_id(chat_id: Union[int, str]) -> Union[int, str]:
        s = str(chat_id).strip()
        try:
            return int(s)
        except ValueError:
            return s

    async def send_text(
        self,
        chat_id: Union[int, str],
        text: str,
        *,
        disable_web_page_preview: bool = True,
        retries: int = 3,
    ) -> None:
        
        chat_id = self._clean_chat_id(chat_id)
        if not text:
            logger.warning("TelegramClient.send_text: empty text -> skip (chat_id=%s)", chat_id)
            return

        delay = 1.0
        for attempt in range(retries):
            try:
                logger.info(
                    "TelegramClient: sending message to %s (%d chars), attempt %d/%d",
                    chat_id, len(text), attempt + 1, retries,
                )
                async with self._lock:
                    await send_markdown_safe_via_telegram(
                        self.bot,
                        chat_id,
                        text,
                        disable_web_page_preview=disable_web_page_preview,
                    )
                logger.info("TelegramClient: sent to %s OK", chat_id)
                return
            except (TimedOut, NetworkError) as e:
                if attempt == retries - 1:
                    logger.exception("TelegramClient: failed after %d retries: %s", retries, e)
                    raise
                logger.warning("TelegramClient: transient error %s, retry in %.1fs", e, delay)
                await asyncio.sleep(delay)
                delay *= 2
