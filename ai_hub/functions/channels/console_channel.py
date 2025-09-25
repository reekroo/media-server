from typing import Any

from .base import Channel

class ConsoleChannel(Channel):
    async def send(self, destination: str, content: str, **kwargs: Any) -> None:
        print("="*20)
        print(f"TO: {destination}")
        print("-"*20)
        print(content)
        print("="*20)