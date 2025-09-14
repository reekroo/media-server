from telegram import Update
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException

from core.settings import Settings

from ..messaging import reply_text_with_markdown
from ..rpc_client import call_mcp_ex, ui_error_message
from ..state import CONVERSATION_STATE, CONVERSATION_HISTORY
from ..models.chat_state import ConversationTurn, ChatState

async def on_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_text = update.message.text
    state = CONVERSATION_STATE.setdefault(chat_id, ChatState())

    if not state.lang:
        try:
            state.lang = detect(user_text)
        except LangDetectException:
            state.lang = Settings().DEFAULT_LANG

    if reply := update.message.reply_to_message:
        prompt = f"Context:\n---\n{reply.text}\n---\nUser question: {user_text}"
        env = await call_mcp_ex("assist.raw_prompt", prompt=prompt)

        if not env.get("ok"):
            await reply_text_with_markdown(update, ui_error_message(env["error"]))
            return

        response = env["result"]
        await reply_text_with_markdown(update, response)
        return

    state.history.append(ConversationTurn(user=user_text, assistant=""))

    if len(state.history) > CONVERSATION_HISTORY:
        state.history.pop(0)

    env = await call_mcp_ex(
        "assist.chat",
        history=[turn.model_dump() for turn in state.history],
    )

    if not env.get("ok"):
        try:
            state.history.pop()
        except Exception:
            pass
        await reply_text_with_markdown(update, ui_error_message(env["error"]))
        return

    response = env["result"]
    state.history[-1].assistant = response
    await reply_text_with_markdown(update, response)
