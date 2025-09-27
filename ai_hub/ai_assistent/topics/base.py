from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from .formatters.base import Formatter

class TopicHandler(ABC):

    @property
    @abstractmethod
    def formatter(self) -> Formatter: ...

    @property
    def empty_response_text(self) -> str:
        return "Sorry, I couldn't come up with a suggestion this time. Please try again."

    @abstractmethod
    def build_prompt(self, payload: Any) -> str: ...
    
    def postprocess(self, llm_text: str) -> str:
        processed_text = (llm_text or "").strip()
        if not processed_text:
            return self.empty_response_text

        return self.formatter.format(processed_text)