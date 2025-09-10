from typing import Protocol, Any

class Channel(Protocol):
    """Абстракция канала доставки (Telegram, Console и т.д.)."""
    async def send(self, destination: str, content: str, **kwargs: Any) -> None:
        ...