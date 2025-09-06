from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class TopicHandler(ABC):
    @abstractmethod
    def build_prompt(self, payload: Any) -> str: ...
    @abstractmethod
    def postprocess(self, llm_text: str) -> Any: ...