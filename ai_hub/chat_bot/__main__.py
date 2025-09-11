import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

# Абсолютные импорты от корня проекта
from core.settings import Settings
from chat_bot.handlers import start_command, digest_command, why_command, on_message_command

async def main() -> None:
    """Запускает Telegram-бота в асинхронном режиме с настроенными таймаутами."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log = logging.getLogger("ChatBot")

    settings = Settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Мы создаем кастомный HTTP-клиент с увеличенными таймаутами
    # connect_timeout: время на установку соединения (именно здесь была ошибка)
    # read_timeout: время на получение ответа после установки соединения
    custom_request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)

    # Передаем наш настроенный клиент в ApplicationBuilder
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).request(custom_request).build()
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---


    # Регистрация обработчиков (без изменений)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("digest", digest_command))
    app.add_handler(CommandHandler("why", why_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message_command))

    # Явная инициализация приложения
    await app.initialize()
    
    # Асинхронный запуск
    await app.updater.start_polling()
    await app.start()

    log.info("ChatBot started successfully with custom timeouts.")
    
    # Бесконечно ждем, чтобы скрипт не завершился
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChatBot stopped by user.")