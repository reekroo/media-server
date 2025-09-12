from telegram import Update
from telegram.ext import ContextTypes

from chat_bot.messaging import reply_text_with_markdown
from chat_bot.rpc_client import call_mcp
from functions.local_data.reader import read_json_async
from core.settings import Settings

async def why_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /why <incident_id>")
        return

    inc_id = context.args[0]
    
    settings = Settings()
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"
    
    incident_data = await read_json_async(inc_path)
    if not incident_data:
        await update.message.reply_text(f"Incident '{inc_id}' not found.")
        return

    await update.message.reply_text("🧠 Analyzing incident...")
    explanation = await call_mcp(
        "assist.digest", 
        kind="clarify", 
        params={"incident": incident_data}
    )
    
    await reply_text_with_markdown(update, explanation)