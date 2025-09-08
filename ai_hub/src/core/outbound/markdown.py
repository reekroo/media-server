from __future__ import annotations
import re

_SPECIALS = r"_*[]()~`>#+-=|{}.!".replace("-", r"\-") 
_SPECIALS_PATTERN = re.compile(r"([_*\[\]\(\)~`>#+\-=|{}.!])")

def _escape_segment_markdown_v2(segment: str) -> str:
    return _SPECIALS_PATTERN.sub(r"\\\1", segment)

def escape_markdown_v2_preserving_code(text: str) -> str:
    if not text:
        return text

    parts: list[str] = []
    i = 0
    n = len(text)

    def find_fence(start: int) -> int:
        idx = text.find("```", start)
        return idx

    while i < n:
        fence_start = find_fence(i)
        if fence_start == -1:
            parts.append(_escape_outside_inline_code(text[i:]))
            break

        if fence_start > i:
            parts.append(_escape_outside_inline_code(text[i:fence_start]))

        fence_end = text.find("```", fence_start + 3)
        if fence_end == -1:
            parts.append(text[fence_start:])
            break

        parts.append(text[fence_start:fence_end + 3])
        i = fence_end + 3

    return "".join(parts)

def _escape_outside_inline_code(segment: str) -> str:
    if not segment:
        return segment

    res: list[str] = []
    in_inline = False
    i = 0
    n = len(segment)

    while i < n:
        ch = segment[i]
        if ch == "`":
            in_inline = not in_inline
            res.append(ch)
            i += 1
            continue

        if not in_inline:
            if _SPECIALS_PATTERN.match(ch):
                res.append("\\" + ch)
            else:
                res.append(ch)
        else:
            res.append(ch)
        i += 1

    return "".join(res)
