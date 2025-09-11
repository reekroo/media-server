from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Используем TYPE_CHECKING для предотвращения циклических импортов
if TYPE_CHECKING:
    from mcp.dispatcher import Dispatcher

from core.settings import Settings
from ai_assistent.service import DigestService
from functions.channels.factory import ChannelFactory

@dataclass(frozen=True)
class AppContext:
    """Контейнер для всех сервисов, который будет передаваться в методы."""
    settings: Settings
    ai_service: DigestService
    channel_factory: ChannelFactory
    dispatcher: Dispatcher