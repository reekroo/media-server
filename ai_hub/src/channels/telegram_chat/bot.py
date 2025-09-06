# src/channels/telegram_chat/bot.py

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder

# Предполагаем, что эти импорты уже существуют и корректны
from ...core.settings import Settings
from ...core.agents.factory import agent_factory
from ...core.router import Orchestrator
from ...topics.clarify import ClarifyIncident
from .handlers_start_help import cmd_start, cmd_help
from .handlers_clarify import cmd_why
from .handlers_chat import on_message

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# <-- НОВАЯ ФУНКЦИЯ для правильной инициализации контекста
async def post_init(application: Application) -> None:
    """Выполняется после создания приложения для добавления данных в контекст."""
    settings = Settings()
    agent = agent_factory(settings)
    topics = {"clarify.incident": ClarifyIncident()}
    orchestrator = Orchestrator(agent, topics)
    
    # Добавляем все сервисы в bot_data. Именно отсюда их будут брать обработчики.
    application.bot_data["settings"] = settings
    application.bot_data["agent"] = agent
    application.bot_data["orchestrator"] = orchestrator
    logger.info("Application context initialized and added to bot_data.")


def main():
    """Initializes and starts the Telegram bot."""
    settings = Settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. The bot cannot start.")
        return

    # --- ИЗМЕНЕНИЕ: Используем .post_init() вместо .data() ---
    app = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Регистрация обработчиков остается без изменений
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("why", cmd_why))
    app.add_handler(CommandHandler("reset", lambda u, c: u.message.reply_text("Context reset (stateless MVP).")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Starting bot polling...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()