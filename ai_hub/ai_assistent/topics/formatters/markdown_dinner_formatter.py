from abc import ABC, abstractmethod
import re

from .base import Formatter

class DinnerFormatter(Formatter):
    _MIN_COUNT = 1
    _MAX_COUNT = 5
    _DEFAULT_COUNT = 3
    _HEADER_RE = re.compile(r'^🍽️ \*Idea\s+(\d+):\s.*?\*$', re.MULTILINE)

    def _normalize_markdown(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text.strip())
        text = re.sub(r"^[•●]\s*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*(\d+)\)\s", r"\1. ", text, flags=re.MULTILINE)
        text = "\n".join(ln.rstrip() for ln in text.splitlines())
        def fix_marks(ln: str) -> str:
            if ln.count("*") % 2: ln = ln.replace("*", "")
            if ln.count("_") % 2: ln = ln.replace("_", "")
            return ln
        return "\n".join(fix_marks(ln) for ln in text.splitlines()).strip()

    def _slice_exact_n_ideas(self, text: str, n: int) -> str:
        matches = list(self._HEADER_RE.finditer(text))
        if not matches:
            return text
        if len(matches) > n:
            cut_at = matches[n].start()
            text = text[:cut_at].rstrip()
        return text

    def format(self, llm_text: str) -> str:
        cleaned = self._normalize_markdown(llm_text)
        
        numbers = [int(m.group(1)) for m in self._HEADER_RE.finditer(cleaned)]
        desired_n = max(numbers) if numbers else self._DEFAULT_COUNT
        desired_n = max(self._MIN_COUNT, min(self._MAX_COUNT, desired_n))
        
        return self._slice_exact_n_ideas(cleaned, desired_n)