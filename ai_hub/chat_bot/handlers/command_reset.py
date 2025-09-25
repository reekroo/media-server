from telegram import Update
from telegram.ext import ContextTypes

from ..messaging import reply_text_with_markdown
from ..state import StateManager

MSG_NO_HISTORY =    "🟧 No conversation history to reset."
MSG_HISTORY_RESET = "✅ Conversation context (history and language) has been reset."

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state_manager: StateManager = context.bot_data["state_manager"]
    
    state_manager: StateManager = context.bot_data["state_manager"]
    if state_manager.pop_chat_state(chat_id):
        await reply_text_with_markdown(update, MSG_HISTORY_RESET)
    else:
        await reply_text_with_markdown(update, MSG_NO_HISTORY)