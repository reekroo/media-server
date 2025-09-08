from __future__ import annotations
from dataclasses import dataclass
from telegram import Bot
from telegram.error import BadRequest

from .markdown import escape_markdown_v2_preserving_code

@dataclass(frozen=True)
class TelegramLimits:
    max_chars: int = 4096
    soft_limit: int = 3900

class TelegramDeliverer:
    def __init__(self, bot: Bot, limits: TelegramLimits) -> None:
        self.bot = bot
        self.limits = limits

    async def send(self, chat_id: int | str, chunk: str, disable_web_page_preview: bool) -> None:
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode="Markdown",
                disable_web_page_preview=disable_web_page_preview,
            )
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                raise

        v2 = escape_markdown_v2_preserving_code(chunk)
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=v2,
                parse_mode="MarkdownV2",
                disable_web_page_preview=disable_web_page_preview,
            )
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                raise

        await self.bot.send_message(
            chat_id=chat_id,
            text=chunk,
            disable_web_page_preview=disable_web_page_preview,
        )

    async def edit(self, chat_id: int | str, message_id: int, text: str, disable_web_page_preview: bool) -> None:
        t = text[: self.limits.max_chars]

        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=t,
                parse_mode="Markdown",
                disable_web_page_preview=disable_web_page_preview,
            )
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                raise

        v2 = escape_markdown_v2_preserving_code(t)
        
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=v2,
                parse_mode="MarkdownV2",
                disable_web_page_preview=disable_web_page_preview,
            )
            return
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                raise

        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=t,
            disable_web_page_preview=disable_web_page_preview,
        )
