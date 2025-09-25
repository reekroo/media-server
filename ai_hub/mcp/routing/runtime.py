from __future__ import annotations
from typing import Any, Dict, List, Optional

from mcp.context import AppContext
from .discovery import list_tools
from .agent_runtime import AgentRuntime

async def chat_with_tools(
    app: AppContext,
    user_text: str,
    lang: Optional[str],
    history: Optional[List[Dict[str, str]]] = None,
) -> Any:
    tools = list_tools()
    runtime = AgentRuntime(app, tools)
    return await runtime.run(user_text, lang, history or [])