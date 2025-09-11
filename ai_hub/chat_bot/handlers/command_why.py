from telegram import Update
from telegram.ext import ContextTypes

from functions.local_data.reader import read_json_async
from core.settings import Settings
from ..rpc_client import call_mcp

async def why_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /why <incident_id>")
        return

    settings = Settings()
    inc_id = context.args[0]
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"
    
    incident_data = await read_json_async(inc_path)
    if not incident_data:
        await update.message.reply_text(f"Incident '{inc_id}' not found.")
        return

    await update.message.reply_text("🧠 Analyzing incident...")
    explanation = await call_mcp("assist.digest", kind="clarify", params={"incident": incident_data})
    await update.message.reply_text(explanation)
    chat_id = update.effective_chat.id
    if chat_id in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY.pop(chat_id)
        await update.message.reply_text("✅ Conversation context has been reset.")
    else:
        await update.message.reply_text("No conversation history to reset.")