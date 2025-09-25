from telegram import Update
from telegram.ext import ContextTypes

from ..rpc_client import ChatRpcClient, ui_error_message
from ..messaging import reply_text_with_markdown

MSG_USAGE = "🟦 Usage: /translate <target_lang> <text to translate>"

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(MSG_USAGE)
        return

    target_lang = context.args[0]
    text_to_translate = " ".join(context.args[1:])

    response = await rpc_client.call(
        "assist.translate", 
        target_lang=target_lang, 
        text=text_to_translate
    )

    if response.get("ok"):
        translated_text = response.get("result", "Error: Empty result from translator.")
        await reply_text_with_markdown(update, translated_text)
    else:
        await reply_text_with_markdown(update, ui_error_message(response.get("error", {})))