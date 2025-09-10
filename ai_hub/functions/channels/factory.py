from .base import Channel
from .telegram_channel import TelegramChannel
from .console_channel import ConsoleChannel

_CHANNELS: dict[str, Channel] = {
    "telegram": TelegramChannel(),
    "console": ConsoleChannel(),
}

class ChannelFactory:
    def get_channel(self, name: str) -> Channel:
        channel = _CHANNELS.get(name.lower())
        if not channel:
            raise ValueError(f"Unknown channel: '{name}'. Available: {list(_CHANNELS.keys())}")
        return channel