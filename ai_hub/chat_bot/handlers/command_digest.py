from telegram import Update
from telegram.ext import ContextTypes

from core.settings import Settings
from functions.channels.telegram_helpers.chunker import Chunker

from ..messaging import reply_text_with_markdown
from ..rpc_client import call_mcp_ex, ui_error_message
from ..state import get_available_digests, CONVERSATION_STATE

UNIVERSAL_NEWS_DIGESTS = {"news", "news_by", "news_tr", "news_eu", "news_us", "news_ru", "news_ua", "news_fun", "gaming", "entertainment"}

MSG_USAGE =           "🟨 Usage: /digest <name>\nAvailable: {available}"
MSG_UNKNOWN_DIGEST =  "🟥 Unknown digest: '{config_name}'.\n\nAvailable: {available}"
MSG_EMPTY_DIGEST   =  "🟥 Digest builder returned empty content."
MSG_BUILDING_DIGEST = "⏳ Building '{config_name}' digest for you..."

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace("_digest", "").replace("_brief", "")
    return f"{target_builder}.{short_func_name}"

def _normalize_payload(payload):
    if payload is None:
        return []
    
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, str) and p.strip()]
    
    if isinstance(payload, str):
        s = payload.strip()
        return [s] if s else []
    
    if isinstance(payload, dict):
        for key in ("items", "texts", "entries", "messages"):
            v = payload.get(key)
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
        s = str(payload).strip()
        return [s] if s else []
    
    s = str(payload).strip()
    return [s] if s else []

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    available_digests = get_available_digests()
    available_text = ", ".join(sorted(available_digests))

    if not context.args:
        await update.message.reply_text(MSG_USAGE.format(available=available_text))
        return

    config_name = "_".join(context.args)
    if config_name not in available_digests:
        await update.message.reply_text(
            MSG_UNKNOWN_DIGEST.format(config_name=config_name, available=available_text)
        )
        return

    rpc_method = _get_rpc_method_name(config_name)
    await reply_text_with_markdown(update, MSG_BUILDING_DIGEST.format(config_name=config_name))

    env = await call_mcp_ex(rpc_method, config_name=config_name)
    if not env.get("ok"):
        await reply_text_with_markdown(update, ui_error_message(env["error"]))
        return

    payload_list = _normalize_payload(env["result"])
    if not payload_list:
        await reply_text_with_markdown(update, MSG_EMPTY_DIGEST)
        return

    settings = Settings()
    chat_id = update.effective_chat.id
    state = CONVERSATION_STATE.get(chat_id)
    user_lang = state.lang if (state and state.lang) else settings.DEFAULT_LANG
    need_translate = user_lang and user_lang.lower() != settings.DEFAULT_LANG.lower()

    chunker = Chunker(soft_limit=3900)

    for digest_text in payload_list:
        for chunk in chunker.split(digest_text or ""):
            text_to_send = chunk
            if need_translate:
                env_tr = await call_mcp_ex("assist.translate", text=chunk, target_lang=user_lang)
                if env_tr.get("ok"):
                    text_to_send = env_tr["result"]
                else:
                    await reply_text_with_markdown(update, ui_error_message(env_tr["error"]))
            await reply_text_with_markdown(update, text_to_send)
