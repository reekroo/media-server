from telegram import Update
from telegram.ext import ContextTypes

from ..rpc_client import call_mcp
from ..state import get_available_digests

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        available = ", ".join(get_available_digests())
        await update.message.reply_text(f"Usage: /digest <name>\nAvailable: {available}")
        return
    
    config_name = context.args[0]
    rpc_method = f"{config_name}.build_digest"

    await update.message.reply_text(f"⏳ Building '{config_name}' digest for you...")

    digest_text = await call_mcp(rpc_method, config_name=config_name)
    
    await update.message.reply_text(digest_text)