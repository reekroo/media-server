from __future__ import annotations
from typing import Optional, Union

from .translator.base import Translator
from .chunker import Chunker
from .deliverer import TelegramDeliverer
from .lang_resolver import TargetLanguageResolver

ChatId = Union[int, str]

class OutboundMediator:
    def __init__(self, translator: Translator, resolver: TargetLanguageResolver, chunker: Chunker, deliverer: TelegramDeliverer) -> None:
        self.translator = translator
        self.resolver = resolver
        self.chunker = chunker
        self.deliverer = deliverer

    async def send_text(
        self,
        chat_id: ChatId,
        text: str,
        *,
        disable_web_page_preview: bool,
        conversation_lang: Optional[str],
    ) -> None:
        target = self.resolver.resolve(conversation_lang, chat_id)
        prepared = await self.translator.translate(text, target)
        for chunk in self.chunker.split(prepared):
            await self.deliverer.send(chat_id, chunk, disable_web_page_preview)

    async def edit_text(
        self,
        chat_id: ChatId,
        message_id: int,
        text: str,
        *,
        disable_web_page_preview: bool,
        conversation_lang: Optional[str],
    ) -> None:
        target = self.resolver.resolve(conversation_lang, chat_id)
        prepared = await self.translator.translate(text, target)
        await self.deliverer.edit(chat_id, message_id, prepared, disable_web_page_preview)
