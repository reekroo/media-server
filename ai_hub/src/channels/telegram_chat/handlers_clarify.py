import json
from pathlib import Path
from ...core.settings import Settings
from ...core.agents.factory import agent_factory
from ...core.router import Orchestrator
from ...topics.clarify import ClarifyIncident

def _orch():
    s = Settings()
    return Orchestrator(agent_factory(s.GEMINI_API_KEY), {"clarify.incident": ClarifyIncident()})

async def cmd_why(update, context):
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: /why <incident_id>")
    inc_id = args[0]
    inc_path = Path(f"state/incidents/{inc_id}.json")
    if not inc_path.exists():
        return await update.message.reply_text("Incident not found.")
    incident = json.loads(inc_path.read_text(encoding="utf-8"))
    orch = _orch()
    text = await orch.run("clarify.incident", {"incident": incident})
    await update.message.reply_text(text[:4000])
