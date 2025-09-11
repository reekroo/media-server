from core.settings import Settings
from .base import Channel
from .telegram_channel import TelegramChannel
from .console_channel import ConsoleChannel

class ChannelFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        # Словарь для хранения классов, а не объектов
        self._channel_classes = {
            "telegram": TelegramChannel,
            "console": ConsoleChannel,
        }
        # Кэш для хранения уже созданных объектов
        self._instances = {}

    def get_channel(self, name: str) -> Channel:
        name = name.lower()
        # Если объект уже создан, возвращаем его из кэша
        if name in self._instances:
            return self._instances[name]

        # Если объекта нет, создаем его
        channel_class = self._channel_classes.get(name)
        if not channel_class:
            raise ValueError(f"Unknown channel: '{name}'.")

        # Создаем экземпляр, передавая ему settings
        if name == "telegram":
            instance = channel_class(settings=self.settings)
        else:
            instance = channel_class()
        
        self._instances[name] = instance
        return instance