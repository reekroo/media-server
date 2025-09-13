from telegram import Update
from telegram.ext import ContextTypes

from chat_bot.messaging import reply_text_with_markdown

from ..state import get_available_digests

HELP_MESSAGE_HEADER = """\
Hi! I'm your AI Hub bot. 🚀

*Available commands:*

• `/help` — Show this message.
• `/reset` — Reset our conversation history.
• `/set_lang <lang>` — Set language for this chat (e.g., en, ru). 
• `/digest <name>` — Trigger a digest build.
• `/why <incident_id>` — Explain a system incident.

*Available digests:*

"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_digests = get_available_digests()
    
    if available_digests:
        digest_commands = "\n".join(f"• `/digest {name}`" for name in available_digests)
        full_help_message = HELP_MESSAGE_HEADER + digest_commands
    else:
        full_help_message = HELP_MESSAGE_HEADER + "_No digests configured yet._"

    await reply_text_with_markdown(update, full_help_message)