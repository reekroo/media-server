from telegram import Update
from telegram.error import BadRequest

async def reply_text_with_markdown(update: Update, text: str) -> None:
    try:
        await update.message.reply_text(text, parse_mode="Markdown")
    except BadRequest as e:
        if "Can't parse entities" in str(e):
            await update.message.reply_text(f"🟨 *Warning: Failed to parse Markdown.*\n\n{text}")
            print(f"Warning: Failed to parse Markdown. Falling back to plain text. Error: {e}")
        else:
            raise e