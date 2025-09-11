from typing import Dict

from ..context import AppContext

async def chat(app: AppContext, history: list[Dict[str, str]]) -> str:
    return await app.ai_service.digest(kind="chat", params={"history": history})