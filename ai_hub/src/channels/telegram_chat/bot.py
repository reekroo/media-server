import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder

from ...container import build_services
from ...core.settings import Settings
from .handlers_start_help import cmd_start, cmd_help
from .handlers_chat import on_message
from .handlers_clarify import cmd_why
from .handlers_triggers import (
    cmd_run_sys, cmd_run_news, cmd_run_media, cmd_run_logs,
    cmd_run_gaming, cmd_run_turkish_news, cmd_run_entertainment, cmd_run_dinner
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    services = build_services()

    application.bot_data["dispatcher"] = services.dispatcher
    application.bot_data["agent"] = services.agent
    application.bot_data["orchestrator"] = services.orchestrator
    application.bot_data["settings"] = services.settings

    logger.info("Application context initialized and added to bot_data.")

def main():
    settings = Settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. The bot cannot start.")
        return

    app = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("why", cmd_why))
    app.add_handler(CommandHandler("reset", lambda u, c: u.message.reply_text("Context reset.")))

    app.add_handler(CommandHandler("run_sys", cmd_run_sys))
    app.add_handler(CommandHandler("run_news", cmd_run_news))
    app.add_handler(CommandHandler("run_media", cmd_run_media))
    app.add_handler(CommandHandler("run_logs", cmd_run_logs))
    app.add_handler(CommandHandler("run_gaming", cmd_run_gaming))
    app.add_handler(CommandHandler("run_news_tr", cmd_run_turkish_news))
    app.add_handler(CommandHandler("run_entertainment", cmd_run_entertainment))
    app.add_handler(CommandHandler("run_dinner", cmd_run_dinner))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Starting bot polling...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()