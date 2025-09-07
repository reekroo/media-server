from functools import wraps
from ...core.settings import Settings

def admin_only(func):

    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        settings: Settings = context.bot_data.get("settings")
        user_id = update.effective_user.id
        
        if settings and str(user_id) in settings.TELEGRAM_ADMIN_IDS:
            return await func(update, context, *args, **kwargs)
        else:
            await update.message.reply_text("⛔️ Sorry, this command is for admins only.")
            
    return wrapped