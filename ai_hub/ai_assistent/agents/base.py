from abc import ABC, abstractmethod
from typing import AsyncIterator

class Agent(ABC):
    name: str

    @abstractmethod
    async def generate(self, prompt: str) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        yield await self.generate(prompt)