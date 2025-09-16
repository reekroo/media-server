from telegram import Update, InputFile
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException
from io import BytesIO
import base64

from core.settings import Settings

from ..messaging import reply_text_with_markdown
from ..rpc_client import call_mcp_ex, ui_error_message
from ..state import CONVERSATION_STATE, CONVERSATION_HISTORY
from ..models.chat_state import ConversationTurn, ChatState

def _history_to_messages(history: list[ConversationTurn]) -> list[dict]:
    messages: list[dict] = []
    for turn in history:
        if turn.user:
            messages.append({"role": "user", "content": turn.user})
        if turn.assistant:
            messages.append({"role": "assistant", "content": turn.assistant})
    return messages

async def _maybe_send_image(update: Update, context: ContextTypes.DEFAULT_TYPE, payload) -> bool:
    if not isinstance(payload, dict) or "b64" not in payload:
        return False

    try:
        image_bytes = base64.b64decode(payload["b64"])
        if not image_bytes:
            return False

        chat_id = update.effective_chat.id
        thread_id = getattr(update.message, "message_thread_id", None) if update.message else None

        bio = BytesIO(image_bytes)
        bio.name = "image.png"
        if thread_id is not None:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=InputFile(bio, filename="image.png"),
                caption=None,
                message_thread_id=thread_id,
            )
        else:
            await update.message.reply_photo(photo=InputFile(bio, filename="image.png"))
        return True
    except Exception:
        return False

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
        if await _maybe_send_image(update, context, response):
            return

        await reply_text_with_markdown(update, str(response))
        return

    state.history.append(ConversationTurn(user=user_text, assistant=""))
    if len(state.history) > CONVERSATION_HISTORY:
        state.history.pop(0)

    history_msgs = _history_to_messages(state.history)

    env = await call_mcp_ex(
        "assist.chat_or_route",
        user_text=user_text,
        lang=state.lang,
        history=history_msgs,
    )

    if not env.get("ok"):
        try:
            state.history.pop()
        except Exception:
            pass
        await reply_text_with_markdown(update, ui_error_message(env["error"]))
        return

    response = env["result"]

    if await _maybe_send_image(update, context, response):
        state.history[-1].assistant = "[image]"
        return

    state.history[-1].assistant = str(response)
    await reply_text_with_markdown(update, str(response))
