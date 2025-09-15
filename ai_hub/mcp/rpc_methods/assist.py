from __future__ import annotations
import base64
from typing import Any, Dict, List, Optional

from mcp.context import AppContext
from mcp.routing.runtime import chat_with_tools

async def translate(app: AppContext, text: str, target_lang: Optional[str]) -> str:
    if not text or not target_lang:
        return text
    return await app.ai_service.translate(text, target_lang=target_lang)

async def chat(app: AppContext, history: List[Dict[str, str]]) -> str:
    return await app.ai_service.digest(kind="chat", params={"history": history})

async def raw_prompt(app: AppContext, prompt: str) -> str:
    return await app.ai_service.agent.generate(prompt)

async def summarize(app: AppContext, text: str, max_chars: int = 220) -> str:
    try:
        return await app.ai_service.digest(kind="summary", params={"text": text, "max_chars": max_chars})
    except Exception:
        text = (text or "").strip()
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1].rstrip() + "…"

async def generate_image_from_summary(app: AppContext, text_summary: str) -> bytes:
    return await app.ai_service.generate_image_from_summary(text_summary)

async def generate_image_from_prompt(app: AppContext, text_summary: str) -> bytes:
    return await app.ai_service.generate_image_from_prompt(text_summary)

async def generate_image_b64_from_summary(app: AppContext, text_summary: str) -> Dict[str, Any]:
    img_bytes = await app.ai_service.generate_image_from_summary(text_summary)
    return {"mime": "image/png", "b64": base64.b64encode(img_bytes).decode("ascii")}

async def generate_image_b64_from_prompt(app: AppContext, text_summary: str) -> Dict[str, Any]:
    img_bytes = await app.ai_service.generate_image_from_prompt(text_summary)
    return {"mime": "image/png", "b64": base64.b64encode(img_bytes).decode("ascii")}

async def chat_or_route(
    app: AppContext,
    user_text: str,
    lang: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    try:
        return await chat_with_tools(app, user_text=user_text, lang=lang, history=history or [])
    except Exception:
        return await app.ai_service.digest(
            kind="chat",
            params={"history": (history or []) + [{"role": "user", "content": user_text}]}
        )
