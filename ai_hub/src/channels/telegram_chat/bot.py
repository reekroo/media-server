from telegram.ext import Application, CommandHandler, MessageHandler, filters
from ...core.settings import Settings
from .handlers_start_help import cmd_start, cmd_help
from .handlers_clarify import cmd_why
from .handlers_chat import on_message

def main():
    s = Settings()
    app = Application.builder().token(s.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("why", cmd_why))
    app.add_handler(CommandHandler("reset", lambda u,c: u.message.reply_text("Context reset (stateless MVP).")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
