from .base import Channel
from typing import Any

class ConsoleChannel(Channel):
    """Канал для вывода сообщений в стандартный stdout."""
    async def send(self, destination: str, content: str, **kwargs: Any) -> None:
        print("="*20)
        print(f"TO: {destination}")
        print("-"*20)
        print(content)
        print("="*20)