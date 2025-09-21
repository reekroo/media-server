from telegram import Update
from telegram.ext import ContextTypes
from typing import List, Optional, Tuple

from core.settings import Settings
from functions.channels.telegram_helpers.chunker import Chunker

from ..messaging import reply_text_with_markdown
from ..rpc_client import ChatRpcClient, ui_error_message
from ..state import get_available_digests, StateManager 

UNIVERSAL_NEWS_DIGESTS = {"news", "news_by", "news_tr", "news_eu", "news_us", "news_ru", "news_ua", "news_fun", "gaming", "entertainment"}

MSG_USAGE =           "🟦 Usage: /digest <name> [count]\nAvailable: {available}"
MSG_UNKNOWN_DIGEST =  "🟥 Unknown digest: '{config_name}'.\n\nAvailable: {available}"
MSG_EMPTY_DIGEST   =  "🟥 Digest builder returned empty content."
MSG_BUILDING_DIGEST = "⏳ Building '{config_name}' digest, please wait..."

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace("_digest", "").replace("_brief", "")
    return f"{target_builder}.{short_func_name}"

def _normalize_payload(payload):
    if payload is None: return []
    if isinstance(payload, list): return [p for p in payload if isinstance(p, str) and p.strip()]
    if isinstance(payload, str): s = payload.strip(); return [s] if s else []
    if isinstance(payload, dict):
        for key in ("items", "texts", "entries", "messages"):
            v = payload.get(key)
            if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
        s = str(payload).strip(); return [s] if s else []
    s = str(payload).strip(); return [s] if s else []

def _parse_digest_args(args: List[str]) -> Tuple[str, Optional[int]]:
    count: Optional[int] = None
    
    if args and args[-1].isdigit():
        count = min(int(args.pop()), 20)

    config_name = "_".join(args)
    return config_name, count

async def _fetch_digest_payload(rpc_client: ChatRpcClient, config_name: str, count: Optional[int]) -> Optional[List[str]]:
    rpc_method = _get_rpc_method_name(config_name)
    rpc_params = {"config_name": config_name}
    if count is not None:
        rpc_params["count"] = count
    
    response = await rpc_client.call(rpc_method, **rpc_params)
    
    if not response.get("ok"):
        return response.get("error")

    payload_list = _normalize_payload(response.get("result"))
    return payload_list

async def _send_payload_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, payload_list: List[str]):
    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    state_manager: StateManager = context.bot_data["state_manager"]

    chat_id = update.effective_chat.id
    state = state_manager.get_chat_state(chat_id)
    user_lang = state.lang if state.lang else settings.DEFAULT_LANGUAGE
    need_translate = user_lang.lower() != settings.DEFAULT_LANGUAGE.lower()

    chunker = Chunker(soft_limit=3900)

    for digest_text in payload_list:
        text_to_process = digest_text or ""
        
        if need_translate and text_to_process:
            tr_response = await rpc_client.call("assist.translate", text=text_to_process, target_lang=user_lang)
            if tr_response.get("ok"):
                text_to_process = tr_response.get("result", text_to_process)
            else:
                await reply_text_with_markdown(update, ui_error_message(tr_response.get("error", {})))
                continue

        for chunk in chunker.split(text_to_process):
            await reply_text_with_markdown(update, chunk)

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]

    available_digests = get_available_digests(settings)
    
    if not context.args:
        await update.message.reply_text(MSG_USAGE.format(available=", ".join(sorted(available_digests))))
        return

    config_name, count = _parse_digest_args(list(context.args))

    if not config_name or config_name not in available_digests:
        await update.message.reply_text(
            MSG_UNKNOWN_DIGEST.format(config_name=config_name, available=", ".join(sorted(available_digests)))
        )
        return

    await reply_text_with_markdown(update, MSG_BUILDING_DIGEST.format(config_name=config_name))

    payload = await _fetch_digest_payload(rpc_client, config_name, count)

    if payload is None:
        await reply_text_with_markdown(update, ui_error_message(payload or {}))
    elif not payload:
        await reply_text_with_markdown(update, MSG_EMPTY_DIGEST)
    else:
        await _send_payload_to_user(update, context, payload)