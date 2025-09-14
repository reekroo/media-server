from telegram import Update
from telegram.ext import ContextTypes

from ..state import CONVERSATION_STATE
from ..messaging import reply_text_with_markdown

MSG_NO_HISTORY =    "🟥 No conversation history to reset."
MSG_HISTORY_RESET = "🟩 Conversation context (history and language) has been reset."

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in CONVERSATION_STATE:
        CONVERSATION_STATE.pop(chat_id)
        await reply_text_with_markdown(update, MSG_HISTORY_RESET)
    else:
        await reply_text_with_markdown(update, MSG_NO_HISTORY)
