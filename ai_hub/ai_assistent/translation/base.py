from __future__ import annotations
from typing import Protocol

class Translator(Protocol):
    async def translate(self, text: str, target_lang: str) -> str: ...
