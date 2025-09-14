from telegram import Update
from telegram.ext import ContextTypes

from chat_bot.messaging import reply_text_with_markdown
from chat_bot.rpc_client import call_mcp
from functions.local_data.reader import read_json_async
from core.settings import Settings

MSG_USAGE =                 "🟥 Usage: /why <incident_id>"
MSG_INCIDENT_NOT_FOUND =    "🟨 Incident '{inc_id}' not found."
MSG_ANALYZING =             "🧠 Analyzing incident..."

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
    
    explanation = await call_mcp(
        "assist.digest", 
        kind="clarify", 
        params={"incident": incident_data}
    )
    
    await reply_text_with_markdown(update, explanation)