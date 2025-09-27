from abc import ABC
import re

from .base import Formatter

class MarkdownDigestFormatter(Formatter):

    def format(self, llm_text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", llm_text).strip()
        
        blocks_raw = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

        def trim(s: str, n: int) -> str:
            s = s.strip()
            return s if len(s) <= n else (s[: n - 1].rstrip() + "…")

        blocks = []
        for b in blocks_raw:
            lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
            if not lines:
                continue

            title = lines[0]
            if "*" not in title:
                clean_title = re.sub(r"^\s*(?:[^\w\s])\s*", "", title)
                title = f"*{clean_title}*"
            
            summary = lines[1] if len(lines) > 1 else ""

            title = trim(title, 80)
            summary = trim(summary, 180)

            block = title if not summary else f"{title}\n{summary}"
            blocks.append(block)

        return "\n\n".join(blocks).strip()
