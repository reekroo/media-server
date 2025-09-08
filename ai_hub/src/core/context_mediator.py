from __future__ import annotations
from typing import Iterable

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest

MAX_TG = 4096
SOFT_LIMIT = 3900

def sanitize_markdown_legacy(text: str) -> str:
    out: list[str] = []
    in_code = False
    i = 0
    while i < len(text):
        ch = text[i]
        prev = text[i - 1] if i > 0 else ""
        if ch == "`" and prev != "\\":
            in_code = not in_code
            out.append(ch)
        else:
            if not in_code and ch in {"[", "]", "_"}:
                out.append("\\" + ch)
            else:
                out.append(ch)
        i += 1
    return "".join(out)

def smart_chunks(text: str, size: int = SOFT_LIMIT) -> Iterable[str]:
    if not text:
        return

    def join_pars(buf: list[str]) -> str:
        return "\n\n".join(buf)

    pars = text.split("\n\n")
    buf: list[str] = []

    for p in pars:
        if len(p) <= size:
            candidate = (join_pars(buf) + ("\n\n" if buf else "") + p) if buf else p
            if len(candidate) <= size:
                buf.append(p)
            else:
                if buf:
                    yield join_pars(buf)
                buf = [p]
            continue

        if buf:
            yield join_pars(buf)
            buf = []

        lines = p.split("\n")
        current = ""
        for line in lines:
            if not current:
                current = line
            elif len(current) + 1 + len(line) <= size:
                current += "\n" + line
            else:
                if current:
                    yield current
                start = 0
                n = len(line)
                while start < n:
                    end = min(start + size, n)
                    cut = line.rfind(" ", start, end)
                    if cut == -1 or cut <= start:
                        cut = end
                    yield line[start:cut]
                    start = cut + (1 if cut < n and line[cut:cut + 1] == " " else 0)
                current = ""
        if current:
            yield current

    if buf:
        out = "\n\n".join(buf)
        if len(out) <= size:
            yield out
        else:
            start = 0
            n = len(out)
            while start < n:
                end = min(start + size, n)
                cut = out.rfind("\n", start, end)
                if cut == -1 or cut <= start:
                    cut = end
                yield out[start:cut]
                start = cut

async def send_markdown_safe_via_telegram(
    bot: Bot,
    chat_id: int | str,
    text: str,
    *,
    disable_web_page_preview: bool = True,
) -> None:
    for chunk in smart_chunks(text):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode='Markdown',
                disable_web_page_preview=disable_web_page_preview,
            )
            continue
        except BadRequest as e:
            if "Can't parse entities" not in str(e):
                raise
        safe = sanitize_markdown_legacy(chunk)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=safe,
                parse_mode='Markdown',
                disable_web_page_preview=disable_web_page_preview,
            )
            continue
        except BadRequest:
            await bot.send_message(
                chat_id=chat_id,
                text=safe,
                disable_web_page_preview=disable_web_page_preview,
            )

async def edit_markdown_safe_via_telegram(
    bot: Bot,
    chat_id: int | str,
    message_id: int,
    text: str,
    *,
    disable_web_page_preview: bool = True,
) -> None:
    t = text[:MAX_TG]
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=t,
            parse_mode='Markdown',
            disable_web_page_preview=disable_web_page_preview,
        )
        return
    except BadRequest as e:
        if "Can't parse entities" not in str(e):
            raise
    safe = sanitize_markdown_legacy(t)
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=safe,
            parse_mode='Markdown',
            disable_web_page_preview=disable_web_page_preview,
        )
    except BadRequest:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=safe,
            disable_web_page_preview=disable_web_page_preview,
        )
