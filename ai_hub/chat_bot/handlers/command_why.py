from telegram import Update
from telegram.ext import ContextTypes

from core.settings import Settings
from functions.local_data.reader import read_json_async

from ..messaging import reply_text_with_markdown
from ..rpc_client import call_mcp_ex, ui_error_message

MSG_USAGE =              "🟥 Usage: /why <incident_id>"
MSG_INCIDENT_NOT_FOUND = "🟨 Incident '{inc_id}' not found."
MSG_ANALYZING =          "🧠 Analyzing incident..."

async def why_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(MSG_USAGE)
        return

    inc_id = context.args[0]

    settings = Settings()
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"

    incident_data = await read_json_async(inc_path)
    if not incident_data:
        await update.message.reply_text(MSG_INCIDENT_NOT_FOUND.format(inc_id=inc_id))
        return

    await update.message.reply_text(MSG_ANALYZING)

    env = await call_mcp_ex(
        "assist.digest",
        kind="clarify",
        params={"incident": incident_data},
    )

    if not env.get("ok"):
        await reply_text_with_markdown(update, ui_error_message(env["error"]))
        return

    explanation = env["result"]
    await reply_text_with_markdown(update, explanation)
