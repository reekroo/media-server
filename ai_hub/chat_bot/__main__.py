import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from core.settings import Settings
from .handlers import start_command, digest_command, why_command, on_message_command

def main():
    """Запускает Telegram-бота."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log = logging.getLogger("ChatBot")

    settings = Settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command)) # help - псевдоним для start
    app.add_handler(CommandHandler("digest", digest_command))
    app.add_handler(CommandHandler("why", why_command))

    # Обработчик для обычных сообщений и ответов на дайджесты
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message_command))

    log.info("ChatBot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()