from abc import ABC, abstractmethod

class Summarizer(ABC):
    
    @abstractmethod
    async def summarize_for_image(self, text: str, max_chars: int) -> str:
        ...