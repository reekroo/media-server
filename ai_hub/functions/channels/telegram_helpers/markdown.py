import re

_SPECIALS_PATTERN = re.compile(r"([_*\[\]()~`>#+\-=|{}.!])")

def _escape_segment(segment: str) -> str:
    return _SPECIALS_PATTERN.sub(r"\\\1", segment)

def escape_markdown_v2_preserving_code(text: str) -> str:
    if not text:
        return ""

    parts = []
    in_code_block = False
    for i, segment in enumerate(text.split("```")):
        if in_code_block:
            parts.append("```" + segment + "```")
        else:
            sub_parts = []
            in_inline_code = False
            for j, sub_segment in enumerate(segment.split("`")):
                if in_inline_code:
                    sub_parts.append("`" + sub_segment + "`")
                else:
                    sub_parts.append(_escape_segment(sub_segment))
                in_inline_code = not in_inline_code
            parts.append("".join(sub_parts))
        in_code_block = not in_code_block

    return "".join(parts)