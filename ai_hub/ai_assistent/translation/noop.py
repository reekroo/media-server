from __future__ import annotations

class NoopTranslator:
    async def translate(self, text: str, target_lang: str) -> str:
        return text
