import re
from telegram import Update, MessageEntity
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from typing import List, Optional, Tuple

from core.settings import Settings
from functions.channels.telegram_helpers.chunker import Chunker
from ..messaging import reply_text_with_markdown
from ..rpc_client import ChatRpcClient, ui_error_message
from ..state import get_available_digests, StateManager 

MSG_USAGE =           "🟦 Usage: /digest <name> [section] [count]\nAvailable: {available}"
MSG_UNKNOWN_DIGEST =  "🟥 Unknown digest: '{config_name}'.\n\nAvailable: {available}"
MSG_EMPTY_DIGEST   =  "🟥 Digest builder returned empty content."
MSG_BUILDING_DIGEST = "⏳ Building '{config_name}' digest, please wait..."

def _normalize_payload(payload):
    if not payload: return []
    if isinstance(payload, list): return [p for p in payload if isinstance(p, str) and p.strip()]
    if isinstance(payload, str): s = payload.strip(); return [s] if s else []
    s = str(payload).strip(); return [s] if s else []

def _parse_digest_args(args: List[str]) -> Tuple[str, Optional[str], Optional[int]]:
    count: Optional[int] = None
    section: Optional[str] = None
    if args and args[-1].isdigit(): count = min(int(args.pop()), 20)
    config_name = args.pop(0) if args else ""
    if args: section = args.pop(0)
    return config_name, section, count

async def _fetch_digest_payload(
    rpc_client: ChatRpcClient, 
    settings: Settings, 
    config_name: str, 
    section: Optional[str], 
    count: Optional[int]
) -> Tuple[Optional[List[str]], Optional[dict]]:
    
    cfg = getattr(settings, config_name, None)
    if not cfg:
        return None, {"message": f"Configuration for '{config_name}' not found."}

    rpc_method = cfg.rpc_method
    
    rpc_params = {"config_name": config_name}
    if count is not None: rpc_params["count"] = count
    if section is not None: rpc_params["section"] = section
    
    response = await rpc_client.call(rpc_method, **rpc_params)
    if not response.get("ok"): return None, response.get("error")
    
    payload_list = _normalize_payload(response.get("result"))
    return payload_list, None

async def _translate_payload_if_needed(
    rpc_client: ChatRpcClient, payload_list: List[str], user_lang: str, default_lang: str
) -> List[str]:
    if user_lang.lower() == default_lang.lower():
        return payload_list
    translated_texts = []
    for text in payload_list:
        if not text: continue
        try:
            tr_response = await rpc_client.call("assist.translate", text=text, target_lang=user_lang)
            translated_texts.append(tr_response.get("result", text) if tr_response.get("ok") else text)
        except Exception:
            translated_texts.append(text)
    return translated_texts

def _prepare_message_for_sending(payload_list: List[str]) -> Tuple[str, List[MessageEntity]]:
    full_text = "\n\n".join(payload_list)
    entities: List[MessageEntity] = []
    for match in re.finditer(r'\*(.*?)\*', full_text):
        start, end = match.span()
        length, offset = len(match.group(1)), start + 1
        entities.append(MessageEntity(type=MessageEntity.ITALIC, offset=offset, length=length))
    plain_text = full_text.replace('*', '')
    return plain_text, entities

async def _send_chunked_message(update: Update, text: str, entities: List[MessageEntity]):
    chunker = Chunker(soft_limit=4000)
    for chunk, chunk_offset in chunker.split_with_offsets(text):
        chunk_entities = []
        for entity in entities:
            if entity.offset < chunk_offset + len(chunk) and entity.offset + entity.length > chunk_offset:
                new_offset, new_length = entity.offset - chunk_offset, entity.length
                if new_offset < 0:
                    new_length += new_offset
                    new_offset = 0
                if new_offset + new_length > len(chunk):
                    new_length = len(chunk) - new_offset
                if new_length > 0:
                    chunk_entities.append(MessageEntity(type=entity.type, offset=new_offset, length=new_length))
        await update.message.reply_text(text=chunk, entities=chunk_entities)

async def _send_payload_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, payload_list: List[str]):
    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    state_manager: StateManager = context.bot_data["state_manager"]
    state = state_manager.get_chat_state(update.effective_chat.id)
    
    translated_payload = await _translate_payload_if_needed(
        rpc_client, payload_list, (state.lang or settings.DEFAULT_LANGUAGE), settings.DEFAULT_LANGUAGE
    )
    plain_text, entities = _prepare_message_for_sending(translated_payload)
    await _send_chunked_message(update, plain_text, entities)

async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    available_digests = get_available_digests(settings)
    
    if not context.args:
        await update.message.reply_text(MSG_USAGE.format(available=", ".join(sorted(available_digests))))
        return

    config_name, section, count = _parse_digest_args(list(context.args))

    if not config_name or config_name not in available_digests:
        await update.message.reply_text(MSG_UNKNOWN_DIGEST.format(config_name=config_name, available=", ".join(sorted(available_digests))))
        return
    
    display_name = f"{config_name} {section or ''}".strip()
    safe_display_name = escape_markdown(display_name, version=2)
    await reply_text_with_markdown(update, MSG_BUILDING_DIGEST.format(config_name=safe_display_name))
    
    payload, error = await _fetch_digest_payload(rpc_client, settings, config_name, section, count)

    if error:
        await reply_text_with_markdown(update, ui_error_message(error))
    elif not payload:
        await reply_text_with_markdown(update, MSG_EMPTY_DIGEST)
    else:
        await _send_payload_to_user(update, context, payload)