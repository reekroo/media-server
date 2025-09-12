from telegram import Update
from telegram.ext import ContextTypes

from chat_bot.messaging import reply_text_with_markdown

from ..state import CONVERSATION_STATE

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in CONVERSATION_STATE:
        CONVERSATION_STATE.pop(chat_id)
        await reply_text_with_markdown(update, "✅ Conversation context (history and language) has been reset.")
    else:
        await reply_text_with_markdown(update, "🟥 No conversation history to reset.")