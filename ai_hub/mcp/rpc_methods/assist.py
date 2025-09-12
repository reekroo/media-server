from mcp.context import AppContext
from typing import Dict, List

async def translate(app: AppContext, text: str, target_lang: str) -> str:
    if not text or not target_lang:
        return text
    return await app.ai_service.translate(text, target_lang=target_lang)

async def chat(app: AppContext, history: List[Dict[str, str]]) -> str:
    return await app.ai_service.digest(kind="chat", params={"history": history})

async def raw_prompt(app: AppContext, prompt: str) -> str:
    return await app.ai_service.agent.generate(prompt)

async def generate_image(app: AppContext, text_summary: str) -> bytes:
    return await app.ai_service.generate_image(text_summary)