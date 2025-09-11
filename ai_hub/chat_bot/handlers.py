from telegram import Update
from telegram.ext import ContextTypes
from .rpc_client import call_mcp

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
from functions.local_data.reader import read_json_async
from core.settings import Settings
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---


HELP_MESSAGE = """\
Hi! I'm your AI Hub bot. 🚀

*Available commands:*
• `/help` — Show this message.
• `/digest <name>` — Trigger a digest build (e.g., `/digest news_by`).
• `/why <incident_id>` — Explain a system incident.

You can also reply to any digest message to ask follow-up questions.
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает сборку дайджеста через MCP."""
    if not context.args:
        await update.message.reply_text("Usage: /digest <name> (e.g., news, gaming, sys)")
        return
    
    config_name = context.args[0]
    method_map = {"news": "news.build", "gaming": "news.build", "entertainment": "news.build", "news_by": "news.build", "news_tr": "news.build"}
    rpc_method = method_map.get(config_name, f"{config_name}.build")

    await update.message.reply_text(f"⏳ Requesting digest '{config_name}' via MCP...")
    await call_mcp(rpc_method, config_name=config_name)

async def why_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Объясняет инцидент, используя 'clarify' топик."""
    if not context.args:
        await update.message.reply_text("Usage: /why <incident_id>")
        return

    settings = Settings()
    inc_id = context.args[0]
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"
    
    incident_data = await read_json_async(inc_path)
    if not incident_data:
        await update.message.reply_text(f"Incident '{inc_id}' not found.")
        return

    await update.message.reply_text("🧠 Analyzing incident...")
    explanation = await call_mcp("assist.digest", kind="clarify", params={"incident": incident_data})
    await update.message.reply_text(explanation)

async def on_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает обычные сообщения и ответы на дайджесты."""
    prompt = update.message.text
    if reply := update.message.reply_to_message:
        prompt = f"Context:\n---\n{reply.text}\n---\nUser question: {prompt}"

    response = await call_mcp("assist.chat", prompt=prompt)
    await update.message.reply_text(response)