from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class TopicHandler(ABC):
    
    @abstractmethod
    def build_prompt(self, payload: Any) -> str: ...
    
    def postprocess(self, llm_text: str) -> str:
        processed_text = (llm_text or "").strip()
        if not processed_text:
            return "Sorry, I couldn't come up with a suggestion this time. Please try again."
        return processed_text