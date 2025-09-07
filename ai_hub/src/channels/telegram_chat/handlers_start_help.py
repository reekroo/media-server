from ...core.settings import Settings
from ...core.dispatcher import DigestDispatcher

HELP_MESSAGE = """\
Hi! I'm your AI Hub bot. 🚀

I can help you in a few ways:

1️⃣ *Direct Chat:* You can ask me any questions right here in our private chat.

2️⃣ *Contextual Replies:* In the group chat where digests are posted, you can reply to any digest message. I'll use the original message as context to provide more details or answer your follow-up questions.

*Available commands:*
• `/help` — Show this help message.
• `/why <incident_id>` — Get a detailed explanation for a system incident.
• `/reset` — Reset the conversation context (useful if my answers start going off-topic).
"""

async def cmd_start(update, context):
    await update.message.reply_text(HELP_MESSAGE)
    
    settings: Settings = context.bot_data.get("settings")
    dispatcher: DigestDispatcher = context.bot_data.get("dispatcher")
    user_id = update.effective_user.id
    is_admin = settings and str(user_id) in settings.TELEGRAM_ADMIN_IDS

    if is_admin and dispatcher:
        try:
            available_jobs = sorted(dispatcher._jobs.keys())            
            admin_commands = [f"• `/run_{job}`" for job in available_jobs]
            
            if admin_commands:
                admin_help_text = (
                    "--- \n"
                    "*Admin Commands:*\n"
                    "You can trigger any digest on demand:\n\n"
                    + "\n".join(admin_commands)
                )
                await update.message.reply_text(admin_help_text, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text("Could not generate the list of admin commands.")

cmd_help = cmd_start
