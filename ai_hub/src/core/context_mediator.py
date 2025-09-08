from __future__ import annotations
from typing import Optional, Dict

from telegram import Bot

# outbound building blocks
from .outbound.lang_resolver import TargetLanguageResolver
from .outbound.translator.base import Translator
from .outbound.translator.noop import NoopTranslator
from .outbound.translator.gemini_sdk_translator import SdkTranslator  # ← используем SDK-адаптер
from .outbound.chunker import Chunker
from .outbound.deliverer import TelegramDeliverer, TelegramLimits
from .outbound.mediator import OutboundMediator

# твои реальные настройки и фабрика агентов
from .settings import Settings
from .agents.factory import agent_factory

_MEDIATOR_CACHE: Dict[int, OutboundMediator] = {}

def _build_mediator(bot: Bot) -> OutboundMediator:
    limits = TelegramLimits()
    chunker = Chunker(limits.soft_limit)
    deliverer = TelegramDeliverer(bot, limits)

    settings = Settings()
    default_lang = settings.DEFAULT_LANG or "en"

    # Translator через твой SDK-агент; если ключа нет — no-op
    translator: Translator
    if getattr(settings, "GEMINI_API_KEY", None):
        agent = agent_factory(settings)          # твой агент на официальном SDK
        translator = SdkTranslator(agent)
    else:
        translator = NoopTranslator()

    # ВРЕМЕННО: не используем язык чата — только conversation_lang → default
    resolver = TargetLanguageResolver(
        default_lang=default_lang,
        chat_lang_lookup=lambda _chat_id: None,  # отключено до внедрения
    )

    return OutboundMediator(translator, resolver, chunker, deliverer)

def _mediator_for(bot: Bot) -> OutboundMediator:
    key = id(bot)
    m = _MEDIATOR_CACHE.get(key)
    if m is None:
        m = _build_mediator(bot)
        _MEDIATOR_CACHE[key] = m
    return m

async def send_markdown_safe_via_telegram(
    bot: Bot,
    chat_id: int | str,
    text: str,
    *,
    disable_web_page_preview: bool = True,
    conversation_lang: Optional[str] = None,
) -> None:
    mediator = _mediator_for(bot)
    await mediator.send_text(
        chat_id,
        text,
        disable_web_page_preview=disable_web_page_preview,
        conversation_lang=conversation_lang,
    )

async def edit_markdown_safe_via_telegram(
    bot: Bot,
    chat_id: int | str,
    message_id: int,
    text: str,
    *,
    disable_web_page_preview: bool = True,
    conversation_lang: Optional[str] = None,
) -> None:
    mediator = _mediator_for(bot)
    await mediator.edit_text(
        chat_id,
        message_id,
        text,
        disable_web_page_preview=disable_web_page_preview,
        conversation_lang=conversation_lang,
    )
