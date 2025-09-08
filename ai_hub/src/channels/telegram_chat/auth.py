from functools import wraps
from ...core.settings import Settings
from ...core.context_mediator import send_markdown_safe_via_telegram

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

def admin_only(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        cfg: Settings | None = context.bot_data.get("settings")
        user_id = update.effective_user.id
        admin_ids = _extract_admin_ids(cfg)
        if str(user_id) in admin_ids:
            return await func(update, context, *args, **kwargs)
        else:
            await send_markdown_safe_via_telegram(
                context.bot,
                update.effective_chat.id,
                "⛔️ Sorry, this command is for admins only.",
            )
            return
    return wrapped
