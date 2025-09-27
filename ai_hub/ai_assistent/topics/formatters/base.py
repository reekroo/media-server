from abc import ABC, abstractmethod

class Formatter(ABC):

    @abstractmethod
    def format(self, llm_text: str) -> str: ...