from telegram import Update
from telegram.ext import ContextTypes

from chat_bot.rpc_client import call_mcp
from chat_bot.state import get_available_digests, CONVERSATION_STATE
from core.settings import Settings

UNIVERSAL_NEWS_DIGESTS = {"news", "news_by", "news_tr", "gaming", "entertainment"}

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace('_digest','').replace('_brief','')
    return f"{target_builder}.{short_func_name}"

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        available = ", ".join(get_available_digests())
        await update.message.reply_text(f"Usage: /digest <name>\nAvailable: {available}")
        return
    
    config_name = context.args[0]
    rpc_method = _get_rpc_method_name(config_name)
    
    await update.message.reply_text(f"⏳ Building '{config_name}' digest for you...")

    digest_text = await call_mcp(rpc_method, config_name=config_name)
    
    settings = Settings()
    chat_id = update.effective_chat.id
    state = CONVERSATION_STATE.get(chat_id)
    user_lang = state.lang if (state and state.lang) else settings.DEFAULT_LANG
    
    if user_lang and user_lang.lower() != settings.DEFAULT_LANG.lower():
        digest_text = await call_mcp(
            "assist.translate", text=digest_text, target_lang=user_lang
        )
        
    await update.message.reply_text(digest_text)