import base64
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from ..rpc_client import call_mcp_ex, ui_error_message
from ..messaging import reply_text_with_markdown

MSG_USAGE       = "🟦 Usage: /image <your text prompt>"
MSG_CLIENT_ERR  = "🟥 A client-side error occurred: `{e}`"
MSG_GENERATING  = "🎨 Generating your image, please wait..."

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(MSG_USAGE); return
    user_prompt = " ".join(context.args).strip()
    if not user_prompt:
        await update.message.reply_text(MSG_USAGE); return

    try:
        await context.bot.send_chat_action(update.effective_chat.id, ChatAction.UPLOAD_PHOTO)
    except Exception:
        pass
    await update.message.reply_text(MSG_GENERATING)

    env = await call_mcp_ex("assist.generate_image_b64_from_prompt", text_summary=user_prompt)
    if not env.get("ok"):
        await reply_text_with_markdown(update, ui_error_message(env["error"]))
        return

    payload = env["result"]

    try:
        if not isinstance(payload, dict) or "b64" not in payload:
            raise RuntimeError(f"Unexpected MCP response shape: {type(payload)}")

        image_bytes = base64.b64decode(payload["b64"])
        if not image_bytes:
            raise RuntimeError("Empty image payload")

        chat_id = update.effective_chat.id
        thread_id = getattr(update.message, "message_thread_id", None) if update.message else None

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
        await reply_text_with_markdown(update, MSG_CLIENT_ERR.format(e=te))
    except Exception as e:
        await reply_text_with_markdown(update, MSG_CLIENT_ERR.format(e=e))
