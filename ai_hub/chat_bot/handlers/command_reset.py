from telegram import Update
from telegram.ext import ContextTypes

from ..state import CONVERSATION_STATE

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in CONVERSATION_STATE:
        CONVERSATION_STATE.pop(chat_id)
        await update.message.reply_text("✅ Conversation context (history and language) has been reset.")
    else:
        await update.message.reply_text("🟥 No conversation history to reset.")