from telegram import Update
from telegram.ext import ContextTypes

from ..state import CONVERSATION_STATE
from ..models.chat_state import ChatState

SUPPORTED_LANGUAGES = {"en", "ru", "by", "ua", "pl", "tr"}

async def set_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not context.args:
        options = ", ".join(SUPPORTED_LANGUAGES)
        await update.message.reply_text(f"Usage: /set_lang <lang_code>\nAvailable: {options}")
        return

    lang_code = context.args[0].lower()
    if lang_code not in SUPPORTED_LANGUAGES:
        await update.message.reply_text(f"🟨 Sorry, '{lang_code}' is not a supported language.")
        return

    state = CONVERSATION_STATE.setdefault(chat_id, ChatState())
    state.lang = lang_code
    
    await update.message.reply_text(f"✅ Language for this chat has been set to: {lang_code}")