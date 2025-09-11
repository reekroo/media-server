from dataclasses import dataclass
from core.settings import Settings
from ai_assistent.service import DigestService
from functions.channels.factory import ChannelFactory

@dataclass(frozen=True)
class AppContext:
    settings: Settings
    ai_service: DigestService
    channel_factory: ChannelFactory