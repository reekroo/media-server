import re

# Специальные символы, которые нужно экранировать в MarkdownV2
_SPECIALS_PATTERN = re.compile(r"([_*\[\]()~`>#+\-=|{}.!])")

def _escape_segment(segment: str) -> str:
    """Экранирует спецсимволы в обычном текстовом сегменте."""
    return _SPECIALS_PATTERN.sub(r"\\\1", segment)

def escape_markdown_v2_preserving_code(text: str) -> str:
    """
    Экранирует текст для MarkdownV2, игнорируя содержимое
    внутри блоков ```code``` и `inline code`.
    """
    if not text:
        return ""

    parts = []
    in_code_block = False
    # Разбиваем текст по блокам кода ```
    for i, segment in enumerate(text.split("```")):
        if in_code_block:
            # Нечетные сегменты - это код, возвращаем как есть с ```
            parts.append("```" + segment + "```")
        else:
            # Четные сегменты - обычный текст, обрабатываем `inline code`
            sub_parts = []
            in_inline_code = False
            for j, sub_segment in enumerate(segment.split("`")):
                if in_inline_code:
                    # Нечетные - inline code, возвращаем как есть с `
                    sub_parts.append("`" + sub_segment + "`")
                else:
                    # Четные - обычный текст, экранируем
                    sub_parts.append(_escape_segment(sub_segment))
                in_inline_code = not in_inline_code
            parts.append("".join(sub_parts))
        in_code_block = not in_code_block

    return "".join(parts)