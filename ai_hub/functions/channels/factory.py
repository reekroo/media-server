from core.settings import Settings
from .base import Channel
from .telegram_channel import TelegramChannel
from .console_channel import ConsoleChannel

class ChannelFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._channel_classes = {
            "telegram": TelegramChannel,
            "console": ConsoleChannel,
        }
        self._instances = {}

    def get_channel(self, name: str) -> Channel:
        name = name.lower()
        if name in self._instances:
            return self._instances[name]

        channel_class = self._channel_classes.get(name)
        if not channel_class:
            raise ValueError(f"Unknown channel: '{name}'.")

        if name == "telegram":
            instance = channel_class(settings=self.settings)
        else:
            instance = channel_class()
        
        self._instances[name] = instance
        return instance