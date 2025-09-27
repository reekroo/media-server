from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.dispatcher.dispatcher import Dispatcher

from core.settings import Settings
from ai_assistent.service import DigestService
from functions.channels.factory import ChannelFactory

@dataclass(frozen=True)
class AppContext:
    settings: Settings
    ai_service: DigestService
    channel_factory: ChannelFactory
    dispatcher: Dispatcher