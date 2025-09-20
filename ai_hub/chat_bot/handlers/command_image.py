import base64
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from ..rpc_client import ChatRpcClient, ui_error_message
from ..messaging import reply_text_with_markdown

log = logging.getLogger(__name__)

MSG_USAGE       = "🟦 Usage: /image <your text prompt>"
MSG_CLIENT_ERR  = "🟥 An error occurred: `{e}`"
MSG_GENERATING  = "🎨 Generating your image, please wait..."

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not context.args:
        await update.message.reply_text(MSG_USAGE)
        return
        
    user_prompt = " ".join(context.args).strip()
    if not user_prompt:
        await update.message.reply_text(MSG_USAGE)
        return

    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]

    try:
        await context.bot.send_chat_action(update.effective_chat.id, ChatAction.UPLOAD_PHOTO)
    except Exception as e:
        log.warning(f"Could not send chat action: {e}")

    await update.message.reply_text(MSG_GENERATING)

    response = await rpc_client.call("assist.generate_image_b64_from_prompt", text_summary=user_prompt)
    if not response.get("ok"):
        await reply_text_with_markdown(update, ui_error_message(response.get("error", {})))
        return

    payload = response.get("result")

    try:
        if not isinstance(payload, dict) or "b64" not in payload:
            raise RuntimeError(f"Unexpected MCP response shape: {type(payload)}")

        image_bytes = base64.b64decode(payload["b64"])
        if not image_bytes:
            raise RuntimeError("Empty image payload")

        chat_id = update.effective_chat.id
        thread_id = update.message.message_thread_id

        if thread_id is not None:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_bytes,
                caption=user_prompt[:1024],
                message_thread_id=thread_id,
            )
        else:
            await update.message.reply_photo(photo=image_bytes, caption=user_prompt[:1024])

    except TelegramError as te:
        log.error(f"Telegram API error while sending photo: {te}", exc_info=True)
        await reply_text_with_markdown(update, MSG_CLIENT_ERR.format(e="Telegram API error, please check logs."))
    except Exception as e:
        log.error(f"Client-side error in image command: {e}", exc_info=True)
        await reply_text_with_markdown(update, MSG_CLIENT_ERR.format(e=e))