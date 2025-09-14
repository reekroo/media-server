from telegram import Update
from telegram.ext import ContextTypes

from core.logging import setup_logger, LOG_FILE_PATH

from ..messaging import reply_text_with_markdown
from ..state import get_available_digests

log = setup_logger(__name__, LOG_FILE_PATH)

HELP_MESSAGE_HEADER = """\
✨ Hi! I'm your *AI Hub bot*.

*Available commands:*

• `/help` — Show this message.
• `/reset` — Reset our conversation history.
• `/set_lang <lang>` — Set language for this chat (e.g., en, ru). 
• `/image <text>` — Generate an image from text.
• `/digest <name>` — Trigger a digest build.
• `/why <incident_id>` — Explain a system incident.

*Available digests:*

"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        log.info(
            "🚨 Start command in chat_id=%s topic_id=%s text=%r",
            update.message.chat_id,
            getattr(update.message, "message_thread_id", None),
            update.message.text,
        )

    available_digests = get_available_digests()

    if available_digests:
        digest_commands = "\n".join(f"• `/digest {name}`" for name in available_digests)
        full_help_message = HELP_MESSAGE_HEADER + digest_commands
    else:
        full_help_message = HELP_MESSAGE_HEADER + "_No digests configured yet._"

    await reply_text_with_markdown(update, full_help_message)
