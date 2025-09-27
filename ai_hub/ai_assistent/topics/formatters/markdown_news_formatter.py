from abc import ABC
import re

from .base import Formatter

class MarkdownNewsFormatter(Formatter):

    def format(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return text

        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        text = "\n".join(ln.rstrip() for ln in text.splitlines())
        return text