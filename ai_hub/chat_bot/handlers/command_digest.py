from telegram import Update
from telegram.ext import ContextTypes

from ..rpc_client import call_mcp
from ..state import get_available_digests

# --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
# Создаем карту, которая связывает команду /digest с правильным RPC-методом в MCP.
METHOD_MAP = {
    # Все "новостные" дайджесты используют один универсальный метод
    "news": "news.build",
    "news_by": "news.build",
    "news_tr": "news.build",
    "gaming": "news.build",
    "entertainment": "news.build",
    
    # Остальные дайджесты имеют свои собственные, уникальные методы
    "sys": "sys.build",
    "media": "media.build",
    "dinner": "dinner.build",
    "daily": "daily.build",
    "logs": "logs.build",
}
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запускает сборку дайджеста, используя карту для выбора правильного RPC-метода.
    """
    if not context.args:
        available = ", ".join(get_available_digests())
        await update.message.reply_text(f"Usage: /digest <name>\nAvailable: {available}")
        return
    
    config_name = context.args[0]
    
    # Ищем нужный метод в нашей карте
    rpc_method = METHOD_MAP.get(config_name)
    
    if not rpc_method:
        await update.message.reply_text(f"Sorry, digest '{config_name}' is not a valid command.")
        return

    await update.message.reply_text(f"⏳ Building '{config_name}' digest for you...")
    
    # Вызываем MCP с правильным именем метода
    digest_text = await call_mcp(rpc_method, config_name=config_name)

    await update.message.reply_text(digest_text)