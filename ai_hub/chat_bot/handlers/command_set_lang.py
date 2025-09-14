from telegram import Update
from telegram.ext import ContextTypes

from ..state import CONVERSATION_STATE
from ..messaging import reply_text_with_markdown
from ..models.chat_state import ChatState

SUPPORTED_LANGUAGES = {"en", "ru", "by", "ua", "pl", "tr"}

MSG_USAGE =              "🟦 Usage: /set_lang <lang_code>\nAvailable: {options}"
MSG_LANG_NOT_SUPPORTED = "🟨 Sorry, '{lang_code}' is not a supported language."
MSG_LANG_SET_SUCCESS =   "🟩 Language for this chat has been set to: {lang_code}"

async def set_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.args:
        options = ", ".join(sorted(SUPPORTED_LANGUAGES))
        await reply_text_with_markdown(update, MSG_USAGE.format(options=options))
        return

    lang_code = context.args[0].lower()
    if lang_code not in SUPPORTED_LANGUAGES:
        await reply_text_with_markdown(update, MSG_LANG_NOT_SUPPORTED.format(lang_code=lang_code))
        return

    state = CONVERSATION_STATE.setdefault(chat_id, ChatState())
    state.lang = lang_code

    await reply_text_with_markdown(update, MSG_LANG_SET_SUCCESS.format(lang_code=lang_code))
