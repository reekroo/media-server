from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional
from datetime import date

from mcp.tools.base import ToolSpec
from mcp.context import AppContext

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

def _pick_tool(tools: List[ToolSpec], name: str) -> Optional[ToolSpec]:
    for t in tools:
        if t.name == name: return t
    lname = (name or "").lower()
    for t in tools:
        if t.name.lower() == lname: return t
    return None

def _parse_json_maybe(s: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(s)
    except Exception: pass
    m = _JSON_RE.search(s or "")
    if not m: return None
    try:
        return json.loads(m.group(0))
    except Exception: return None

class AgentRuntime:
    def __init__(self, app: AppContext, tools: List[ToolSpec]):
        self.app = app
        self.tools = tools
        self.agent = app.ai_service.agent

    async def run(self, user_text: str, lang: Optional[str], history: List[Dict[str, str]]) -> Any:
        prompt = self._build_prompt(user_text, history)
        raw_response = await self.agent.generate(prompt)
        decision_data = _parse_json_maybe(raw_response) or {}

        if (decision_data.get("decision") or "").lower() == "tool":
            tool_name = decision_data.get("tool_name")
            args = decision_data.get("arguments") or {}
            spec = _pick_tool(self.tools, tool_name or "")
            
            result = await self._execute_tool(spec, args, user_text, history)
            return await self._postprocess_tool_result(result, lang, spec)
        else:
            chat_text = decision_data.get("text")
            return await self._get_chat_response(chat_text, lang, user_text, history)

    def _build_prompt(self, user_text: str, history: List[Dict[str, str]]) -> str:
        hist_block = self._render_history(history)
        history_section = f"Conversation so far:\n{hist_block}\n\n" if hist_block else ""
        today_date = date.today().strftime('%Y-%m-%d')
        system_prompt = (
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
            f"- Today's date is {today_date}. Use this to resolve any relative date references from the user."
            "When you need information about news or weather, use the available tools."
        )
        manifest = self._manifest_for_llm()
        return (
            f"{system_prompt}\n"
            f"Available tools:\n{manifest}\n\n"
            f"{history_section}"
            f"New user message:\n{user_text}\n\n"
            "Return JSON like:\n"
            "{\"decision\":\"tool|chat\", \"tool_name\":\"<name or null>\", \"arguments\":{}, \"text\":\"<final message for chat or omit>\"}"
        )
    
    async def _execute_tool(self, spec: Optional[ToolSpec], args: Dict, user_text: str, history: List[Dict[str, str]]) -> Any:
        if not spec:
            return await self.app.ai_service.digest(
                kind="chat", params={"history": history + [{"role": "user", "content": user_text}]}
            )
        return await spec.execute(self.app, args)

    async def _postprocess_tool_result(self, result: Any, lang: Optional[str], spec: Optional[ToolSpec]) -> Any:
        if isinstance(result, list):
            result = "\n\n".join([str(s) for s in result if s and str(s).strip()]) or "No content."
        if isinstance(result, dict) and ("b64" in result or result.get("type") == "image"):
            return result
        if not isinstance(result, str):
            result = str(result)
        
        if lang and spec and spec.name != "text_translator":
            result = await self.app.ai_service.translate(result, target_lang=lang)
        return result

    async def _get_chat_response(self, text: Optional[str], lang: Optional[str], user_text: str, history: List[Dict[str, str]]) -> str:
        if not text:
            text = await self.app.ai_service.digest(
                kind="chat", params={"history": history + [{"role": "user", "content": user_text}]}
            )
        if lang and isinstance(text, str):
            text = await self.app.ai_service.translate(text, target_lang=lang)
        return text

    def _manifest_for_llm(self) -> str:
        parts = []
        for t in self.tools:
            parts.append(
                f"- name: {t.name}\n"
                f"  description: {t.description}\n"
                f"  json_schema: {json.dumps(t.parameters_json_schema, ensure_ascii=False)}"
            )
        return "\n".join(parts)
    
    def _render_history(self, history: List[Dict[str, str]], max_pairs: int = 6) -> str:
        trimmed = history[-(max_pairs * 2):] if history else []
        lines = []
        for msg in trimmed:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip()
            if not content: continue
            prefix = "User" if role == "user" else "Assistant"
            lines.append(f"{prefix}: {content}")
        return "\n".join(lines)