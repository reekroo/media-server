from abc import ABC

from .base import Formatter

class SimpleTextFormatter(Formatter):
    def format(self, llm_text: str) -> str:
        return llm_text