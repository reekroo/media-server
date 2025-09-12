from typing import Dict

from ..context import AppContext

async def chat(app: AppContext, history: list[Dict[str, str]]) -> str:
    return await app.ai_service.digest(kind="chat", params={"history": history})

async def translate(app: AppContext, text: str, target_lang: str) -> str:
    if not text or not target_lang:
        return text
    return await app.ai_service.translate(text, target_lang=target_lang)