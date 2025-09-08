from ...core.settings import Settings
from ...core.dispatcher import DigestDispatcher
from ...core.context_mediator import send_markdown_safe_via_telegram

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

def _extract_admin_ids(cfg: Settings | None) -> set[str]:
    if not cfg:
        return set()
    
    val = getattr(cfg, "TELEGRAM_ADMIN_IDS", [])
    
    if isinstance(val, str):
        return set(s.strip() for s in val.split(",") if s.strip())
    
    try:
        return set(map(str, val))
    except TypeError:
        return set()

async def cmd_start(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id

    await send_markdown_safe_via_telegram(bot, chat_id, HELP_MESSAGE)

    cfg: Settings | None = context.bot_data.get("settings")
    dispatcher: DigestDispatcher | None = context.bot_data.get("dispatcher")
    user_id = update.effective_user.id
    admin_ids = _extract_admin_ids(cfg)
    is_admin = str(user_id) in admin_ids

    if is_admin and dispatcher:
        try:
            available_jobs = sorted(dispatcher._jobs.keys())
            if available_jobs:
                admin_commands = [f"• `/run_{job}`" for job in available_jobs]
                admin_help_text = (
                    "*Admin Commands:*\n"
                    "You can trigger any digest on demand:\n\n"
                    + "\n".join(admin_commands)
                )
                await send_markdown_safe_via_telegram(bot, chat_id, admin_help_text)
        except Exception:
            await send_markdown_safe_via_telegram(
                bot, chat_id, "Could not generate the list of admin commands."
            )

cmd_help = cmd_start
