HELP_MESSAGE = """\
Hi! I'm your AI Hub bot. 🚀

I can help you in a few ways:

1️⃣ **Direct Chat:** You can ask me any questions right here in our private chat.

2️⃣ **Contextual Replies:** In the group chat where digests are posted, you can reply to any digest message. I'll use the original message as context to provide more details or answer your follow-up questions.

**Available commands:**
• `/help` — Show this help message.
• `/why <incident_id>` — Get a detailed explanation for a system incident.
• `/reset` — Reset the conversation context (useful if my answers start going off-topic).
"""

async def cmd_start(update, context):
    await update.message.reply_text(HELP_MESSAGE)
cmd_help = cmd_start
