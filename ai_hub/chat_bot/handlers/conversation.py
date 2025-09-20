from telegram import Update, InputFile
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException
from io import BytesIO
import base64
import logging

from core.settings import Settings
from ..messaging import reply_text_with_markdown
from ..rpc_client import ChatRpcClient, ui_error_message
from ..state import StateManager
from ..models.chat_state import ConversationTurn

log = logging.getLogger(__name__)

def _history_to_messages(history: list[ConversationTurn]) -> list[dict]:
    messages: list[dict] = []
    for turn in history:
        if turn.user: messages.append({"role": "user", "content": turn.user})
        if turn.assistant: messages.append({"role": "assistant", "content": turn.assistant})
    return messages

async def _maybe_send_image(update: Update, context: ContextTypes.DEFAULT_TYPE, payload) -> bool:
    if not isinstance(payload, dict) or "b64" not in payload: return False
    try:
        image_bytes = base64.b64decode(payload["b64"])
        if not image_bytes: return False
        chat_id = update.effective_chat.id
        thread_id = update.message.message_thread_id if update.message else None
        bio = BytesIO(image_bytes); bio.name = "image.png"
        if thread_id is not None:
            await context.bot.send_photo(chat_id=chat_id, photo=InputFile(bio, filename="image.png"), message_thread_id=thread_id)
        else:
            await update.message.reply_photo(photo=InputFile(bio, filename="image.png"))
        return True
    except Exception as e:
        log.error(f"Failed to send image: {e}", exc_info=True)
        return False


async def on_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    state_manager: StateManager = context.bot_data["state_manager"]

    chat_id = update.effective_chat.id
    user_text = update.message.text
    state = state_manager.get_chat_state(chat_id)

    if not state.lang:
        try:
            state.lang = detect(user_text)
        except LangDetectException:
            state.lang = settings.DEFAULT_LANG
        state_manager.save_chat_state(chat_id, state)

    if reply := update.message.reply_to_message:
        prompt = f"Context:\n---\n{reply.text}\n---\nUser question: {user_text}"
        response_env = await rpc_client.call("assist.raw_prompt", prompt=prompt)

        if not response_env.get("ok"):
            await reply_text_with_markdown(update, ui_error_message(response_env.get("error", {})))
            return

        response = response_env.get("result")
        if await _maybe_send_image(update, context, response):
            return

        await reply_text_with_markdown(update, str(response))
        return

    state.history.append(ConversationTurn(user=user_text, assistant=""))
    if len(state.history) > state_manager.history_limit:
        state.history.pop(0)

    history_msgs = _history_to_messages(state.history)

    response_env = await rpc_client.call(
        "assist.chat_or_route", user_text=user_text, lang=state.lang, history=history_msgs,
    )

    if not response_env.get("ok"):
        try:
            state.history.pop()
            state_manager.save_chat_state(chat_id, state)
        except IndexError:
            pass
        await reply_text_with_markdown(update, ui_error_message(response_env.get("error", {})))
        return

    response = response_env.get("result")

    if await _maybe_send_image(update, context, response):
        state.history[-1].assistant = "[image]"
    else:
        state.history[-1].assistant = str(response)

    state_manager.save_chat_state(chat_id, state)

    if isinstance(response, str):
        await reply_text_with_markdown(update, response)