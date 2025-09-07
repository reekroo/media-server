import json
from ...core.router import Orchestrator
from ...core.settings import Settings

async def cmd_why(update, context):
    orchestrator: Orchestrator = context.bot_data.get("orchestrator")
    settings: Settings = context.bot_data.get("settings")

    if not (orchestrator and settings):
        await update.message.reply_text("Error: Core components are not configured.")
        return

    if not context.args:
        return await update.message.reply_text("Usage: /why <incident_id>")
    
    inc_id = context.args[0]
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"
    
    if not inc_path.exists():
        return await update.message.reply_text("Incident not found.")
        
    try:
        incident_data = json.loads(inc_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        return await update.message.reply_text(f"Could not read incident data: {e}")

    text = await orchestrator.run("clarify.incident", {"incident": incident_data})
    await update.message.reply_text(text[:4000])