import base64
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from chat_bot.rpc_client import call_mcp
from chat_bot.messaging import reply_text_with_markdown

MSG_USAGE =         "🟦 Usage: /image <your text prompt>"
MSG_CLIENT_ERROR =  "🟥 A client-side error occurred: `{e}`"
MSG_GENERATING =    "🎨 Generating your image, please wait..."

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(MSG_USAGE)
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    await update.message.reply_text(MSG_GENERATING)

    user_prompt = " ".join(context.args)
    base64_image, error = await call_mcp("assist.generate_image_from_prompt", text_summary=user_prompt)

    if error:
        await reply_text_with_markdown(update, error)
        return

    try:
        image_bytes = base64.b64decode(base64_image)
        await update.message.reply_photo(photo=image_bytes)
    except Exception as e:
        await reply_text_with_markdown(update, MSG_CLIENT_ERROR.format(e=e))