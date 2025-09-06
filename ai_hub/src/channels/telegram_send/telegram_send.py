from __future__ import annotations
import asyncio, os
from typing import Iterable
from telegram import Bot
from telegram.error import TimedOut, NetworkError
from telegram.request import HTTPXRequest

MAX = 4096

def _clean(s: str) -> str:
    return (s or "").strip()

def _chunks(text: str, size: int = MAX) -> Iterable[str]:
    if not text:
        yield " "
        return
    for i in range(0, len(text), size):
        yield text[i:i+size]

def _build_bot(token: str) -> Bot:
    # минимальный набор параметров, совместимый с PTB >=20
    req = HTTPXRequest(
        connect_timeout=15.0,  # время на установку TCP
        read_timeout=30.0,     # ожидание ответа
    )
    return Bot(token=token, request=req)

async def _send_with_retries(bot: Bot, chat_id: str, text: str, *, retries: int = 3) -> None:
    delay = 1.0
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
            return
        except (TimedOut, NetworkError) as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2  # экспоненциальная пауза

async def send_text(token: str, chat_id: str, text: str) -> None:
    token = _clean(token)
    chat_id = _clean(chat_id)
    bot = _build_bot(token)
    for chunk in _chunks(text, MAX):
        await _send_with_retries(bot, chat_id, chunk, retries=4)
