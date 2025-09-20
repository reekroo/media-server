import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from core.settings import Settings
from core.logging import setup_logger, LOG_FILE_PATH
from chat_bot.rpc_client import ChatRpcClient
from chat_bot.state import StateManager

from chat_bot.handlers.command_digest import digest_command
from chat_bot.handlers.command_reset import reset_command
from chat_bot.handlers.command_start import start_command
from chat_bot.handlers.command_why import why_command
from chat_bot.handlers.command_set_lang import set_lang_command
from chat_bot.handlers.conversation import on_message_command
from chat_bot.handlers.command_image import image_command 

log = setup_logger(__name__, LOG_FILE_PATH)

async def main() -> None:
    settings = Settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return

    app = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .request(HTTPXRequest(connect_timeout=30.0, read_timeout=30.0))
        .build()
    )

    log.info("Populating bot_data manually...")
    app.bot_data["settings"] = settings
    app.bot_data["rpc_client"] = ChatRpcClient(settings)
    app.bot_data["state_manager"] = StateManager(settings)
    log.info("bot_data populated successfully.")

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("digest", digest_command))
    app.add_handler(CommandHandler("why", why_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("set_lang", set_lang_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message_command))

    try:
        await app.initialize()
        await app.updater.start_polling()
        await app.start()
        log.info("ChatBot started successfully.")
        await asyncio.Event().wait()
    finally:
        log.info("Shutting down ChatBot...")
        if app.updater and getattr(app.updater, '_running', False):
            await app.updater.stop()
        if app.is_running():
            await app.stop()
        await app.shutdown()
        log.info("ChatBot shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChatBot stopping...")