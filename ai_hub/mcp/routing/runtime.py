from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional

from .discovery import list_tools
from mcp.tools.base import ToolSpec

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

def _manifest_for_llm(tools: List[ToolSpec]) -> str:
    parts = []
    for t in tools:
        parts.append(
            f"- name: {t.name}\n"
            f"  description: {t.description}\n"
            f"  json_schema: {json.dumps(t.parameters_json_schema, ensure_ascii=False)}"
        )
    return "\n".join(parts)

def _pick_tool(tools: List[ToolSpec], name: str) -> Optional[ToolSpec]:
    for t in tools:
        if t.name == name:
            return t
    lname = (name or "").lower()
    for t in tools:
        if t.name.lower() == lname:
            return t
    return None

def _parse_json_maybe(s: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(s)
    except Exception:
        pass
    m = _JSON_RE.search(s or "")
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def _render_history(history: List[Dict[str, str]], max_pairs: int = 6) -> str:
    trimmed = history[-(max_pairs * 2):] if history else []
    lines = []
    for msg in trimmed:
        role = msg.get("role", "user")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {content}")
    return "\n".join(lines)

async def chat_with_tools(
    app: "AppContext",
    user_text: str,
    lang: Optional[str],
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    tools = list_tools()
    agent = app.ai_service.agent
    hist_block = _render_history(history or [], max_pairs=6)
    history_section = f"Conversation so far:\n{hist_block}\n\n" if hist_block else ""

    system = (
        "You are an intent router and assistant. The user message may be in ANY language.\n"
        "You have access to a small set of functions (tools). "
        "Choose EXACTLY ONE of the following options:\n"
        "  1) If one tool clearly fits, set decision='tool', specify tool_name and JSON arguments.\n"
        "  2) If no tool fits, set decision='chat' and write the final answer in user's language.\n\n"
        "IMPORTANT RULES:\n"
        "- Respond with JSON ONLY. No commentary, no markdown, no code fences.\n"
        "- Keep arguments minimal; if none are needed, use an empty object.\n"
        "- If decision='tool', do not include 'text'.\n"
        "- If decision='chat', put the final answer into 'text'.\n"
    )
    manifest = _manifest_for_llm(tools)
    prompt = (
        f"{system}\n"
        f"Available tools:\n{manifest}\n\n"
        f"{history_section}"
        f"New user message:\n{user_text}\n\n"
        "Return JSON like:\n"
        "{"
        "\"decision\":\"tool|chat\", "
        "\"tool_name\":\"<name or null>\", "
        "\"arguments\":{}, "
        "\"text\":\"<final message for chat or omit>\""
        "}"
    )

    raw = await agent.generate(prompt)
    data = _parse_json_maybe(raw) or {}
    decision = (data.get("decision") or "").lower()

    if decision == "tool":
        tool_name = data.get("tool_name")
        args = data.get("arguments") or {}
        spec = _pick_tool(tools, tool_name or "")
        if not spec:
            result = await app.ai_service.digest(
                kind="chat",
                params={"history": (history or []) + [{"role": "user", "content": user_text}]}
            )
        else:
            result = await spec.execute(app, args)

        if lang:
            result = await app.ai_service.translate(result, target_lang=lang)
        return result

    text = data.get("text")
    if not text:
        text = await app.ai_service.digest(
            kind="chat",
            params={"history": (history or []) + [{"role": "user", "content": user_text}]}
        )
    if lang:
        text = await app.ai_service.translate(text, target_lang=lang)
    return text
