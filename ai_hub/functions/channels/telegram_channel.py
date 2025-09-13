import asyncio
from typing import Any
from telegram import Bot
from telegram.error import TimedOut, NetworkError, BadRequest, ChatMigrated, RetryAfter
from telegram.request import HTTPXRequest

from .base import Channel
from .telegram_helpers.chunker import Chunker
from core.settings import Settings
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

def _trim_markdown_caption(str: str, limit: int = 1024) -> str:
    if not str: return str
    if len(str) <= limit: return str
    
    str = str[:limit]
    while str and str[-1] in ("*", "_", "`"):
        str = str[:-1]
    return str

class TelegramChannel(Channel):
    def __init__(self, settings: Settings, timeout: float = 25.0):
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
        current_destination = destination

        for attempt in range(retries):
            try:
                async with self._lock:
                    for chunk in self.chunker.split(content):
                        await self._deliver_chunk(current_destination, chunk, kwargs)
                log.info(f"Successfully sent message to {current_destination}")
                return
            
            except ChatMigrated as e:
                new_chat_id = e.new_chat_id
                log.warning(
                    f"Chat ID {current_destination} has migrated to {new_chat_id}. "
                    f"Please update your config files! Retrying with new ID..."
                )
                current_destination = str(new_chat_id)
                continue

            except (TimedOut, NetworkError) as e:
                if attempt == retries - 1:
                    log.exception(f"Telegram send failed after {retries} retries")
                    raise
                log.warning(f"Telegram transient error: {e}, retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2

    async def _deliver_chunk(self, chat_id: str, chunk: str, kwargs: dict) -> None:
        disable_preview = kwargs.get("disable_web_page_preview", True)
        topic_id = kwargs.get("destination_topic") 
        
        try:
            await self.bot.send_message(
                chat_id, 
                chunk, 
                parse_mode="Markdown", 
                disable_web_page_preview=disable_preview,
                message_thread_id=topic_id
            )
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                log.error(f"Unhandled BadRequest error: {e}")
                raise

        await self.bot.send_message(
            chat_id, 
            chunk, 
            disable_web_page_preview=disable_preview,
            message_thread_id=topic_id
        )

    async def send_photo(self, destination: str, image_bytes: bytes, caption: str, **kwargs: Any) -> None:
        log.info(f"Sending photo to {destination} with caption of {len(caption)} chars")
        
        topic_id = kwargs.get("destination_topic") 
        caption_chunker = Chunker(soft_limit=1024)
        caption_chunks = iter(caption_chunker.split(caption))
        first_chunk = next(caption_chunks, "")
        first_chunk = _trim_markdown_caption(first_chunk)

        try:
            await self.bot.send_photo(
                chat_id=destination,
                photo=image_bytes,
                caption=first_chunk,
                parse_mode="Markdown",
                message_thread_id=topic_id
            )
            
            for chunk in caption_chunks:
                await self.send(destination, chunk, **kwargs)

        except BadRequest as e:
            if "Can't parse entities" in str(e):
                log.warning(f"Failed to send photo with formatted caption (error: {e}). Falling back.")
                await self.bot.send_photo(chat_id=destination, photo=image_bytes)
                await self.send(destination, caption, **kwargs)
            else:
                raise e