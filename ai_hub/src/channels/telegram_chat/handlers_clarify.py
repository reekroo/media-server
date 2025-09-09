import json
from ...core.router import Orchestrator
from ...core.settings import Settings
from ...core.context_mediator import send_markdown_safe_via_telegram

async def cmd_why(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id

    orchestrator: Orchestrator | None = context.bot_data.get("orchestrator")
    cfg: Settings | None = context.bot_data.get("settings")

    if not (orchestrator and cfg):
        await send_markdown_safe_via_telegram(bot, chat_id, "Error: Core components are not configured.")
        return

    if not context.args:
        await send_markdown_safe_via_telegram(bot, chat_id, "Usage: /why <incident_id>")
        return

    inc_id = context.args[0]
    inc_path = cfg.STATE_DIR / "incidents" / f"{inc_id}.json"

    if not inc_path.exists():
        await send_markdown_safe_via_telegram(bot, chat_id, "Incident not found.")
        return

    try:
        incident_data = json.loads(inc_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        await send_markdown_safe_via_telegram(bot, chat_id, f"Could not read incident data: {e}")
        return

    text = await orchestrator.run("clarify.incident", {"incident": incident_data})
    await send_markdown_safe_via_telegram(bot, chat_id, text or "No details available.")
