import logging
from .auth import admin_only
from ...core.dispatcher import DigestDispatcher

logger = logging.getLogger(__name__)

async def _run_digest(update, context, digest_name: str, **kwargs):
    dispatcher: DigestDispatcher = context.bot_data.get("dispatcher")
    if not dispatcher:
        await update.message.reply_text("Error: DigestDispatcher is not configured.")
        return

    msg = await update.message.reply_text(f"⏳ Starting '{digest_name}' digest generation...")
    
    try:
        results = await dispatcher.run(name=digest_name, **kwargs)
        
        if not results or not any(res.strip() for res in results):
            final_text = f"✅ Job '{digest_name}' ran successfully but produced no output."
        else:
            final_text = "\n\n---\n\n".join(results)

        await context.bot.edit_message_text(
            text=final_text[:4096],
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )
    except Exception as e:
        logger.exception(f"Failed to run digest '{digest_name}' via command.")
        await context.bot.edit_message_text(
            text=f"❌ An error occurred while running '{digest_name}':\n\n`{e}`",
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )

@admin_only
async def cmd_run_sys(update, context):
    await _run_digest(update, context, "sys")

@admin_only
async def cmd_run_news(update, context):
    section = context.args[0] if context.args else None
    await _run_digest(update, context, "news", section=section)
    
@admin_only
async def cmd_run_media(update, context):
    await _run_digest(update, context, "media")

@admin_only
async def cmd_run_logs(update, context):
    await _run_digest(update, context, "logs")

@admin_only
async def cmd_run_gaming(update, context):
    await _run_digest(update, context, "gaming")

@admin_only
async def cmd_run_turkish_news(update, context):
    await _run_digest(update, context, "news_tr")

@admin_only
async def cmd_run_entertainment(update, context):
    await _run_digest(update, context, "entertainment")

@admin_only
async def cmd_run_dinner(update, context):
    await _run_digest(update, context, "dinner")