from __future__ import annotations
import asyncio
import logging
from typing import Iterable
from telegram import Bot
from telegram.error import TimedOut, NetworkError
from telegram.request import HTTPXRequest

MAX_CHUNK_SIZE = 4096
logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self, token: str):
        self._token = (token or "").strip()
        if not self._token:
            raise ValueError("Telegram bot token cannot be empty.")
        
        req = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0)
        self.bot = Bot(token=self._token, request=req)

    async def send_text(self, chat_id: str, text: str) -> None:
        if not text or not text.strip():
            logger.warning("Attempted to send an empty or whitespace-only message. Aborting.")
            return

        clean_chat_id = (chat_id or "").strip()
        if not clean_chat_id:
            return

        for chunk in self._chunk_text(text):
            await self._send_with_retries(clean_chat_id, chunk, retries=4)

    async def _send_with_retries(self, chat_id: str, text: str, *, retries: int = 3) -> None:
        delay = 1.0
        
        for attempt in range(retries):
            try:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    disable_web_page_preview=True, 
                    parse_mode='Markdown'
                )
                return
            except (TimedOut, NetworkError):
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(delay)
                delay *= 2

    @staticmethod
    def _chunk_text(text: str, size: int = MAX_CHUNK_SIZE) -> Iterable[str]:
        for i in range(0, len(text), size):
            yield text[i:i + size]