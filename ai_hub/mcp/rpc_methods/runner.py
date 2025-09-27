import asyncio
from typing import Any, List, Optional, Union

from mcp.context import AppContext
from mcp.dispatcher import Dispatcher
from core.logging import setup_logger, LOG_FILE_PATH
from core.constants.news import UNIVERSAL_NEWS_DIGESTS

log = setup_logger(__name__, LOG_FILE_PATH)

TELEGRAM_CAPTION_LIMIT = 1024

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace('_digest','').replace('_brief','')
    return f"{target_builder}.{short_func_name}"

async def _send_digest_as_text(app: AppContext, cfg: Any, digest_text: str) -> None:
    channel = app.channel_factory.get_channel(cfg.to)
    await channel.send(
        destination=cfg.destination_group, 
        content=digest_text, 
        destination_topic=cfg.destination_topic
    )

async def _send_digest_with_image(app: AppContext, cfg: Any, digest_text: str, image_bytes: bytes, config_name: str) -> None:
    channel = app.channel_factory.get_channel(cfg.to)
    try:
        if len(digest_text) <= TELEGRAM_CAPTION_LIMIT:
            log.info(f"Sending photo with caption for '{config_name}'")
            await channel.send_photo(
                destination=cfg.destination_group, 
                image_bytes=image_bytes,
                caption=digest_text, 
                destination_topic=cfg.destination_topic
            )
        else:
            log.info(f"Caption for '{config_name}' is too long. Sending as separate messages.")
            photo_message = await channel.send_photo(
                destination=cfg.destination_group, 
                image_bytes=image_bytes,
                caption="", 
                destination_topic=cfg.destination_topic
            )
            
            reply_id = photo_message.message_id if photo_message else None

            await channel.send(
                destination=cfg.destination_group, 
                content=digest_text,
                destination_topic=cfg.destination_topic, 
                reply_to_message_id=reply_id
            )
    except Exception as e:
        log.error(f"Failed to send photo for '{config_name}': {e}", exc_info=True)
        error_message = f"⚠️ _Image was generated, but failed to send._\n\n{digest_text}"
        await _send_digest_as_text(app, cfg, error_message)

async def _get_translated_text_task(app: AppContext, text: str, cfg: Any) -> str:
    target_lang = getattr(cfg, "destination_language", None)
    if not target_lang or target_lang.lower() == app.settings.DEFAULT_LANGUAGE.lower():
        return text
    
    log.info(f"Translating digest to '{target_lang}'...")
    try:
        return await app.dispatcher.run("assist.translate", text=text, target_lang=target_lang)
    except Exception as e:
        log.error(f"Translation task failed: {e}", exc_info=True)
        return text

async def _get_image_bytes_task(app: AppContext, text: str) -> Optional[bytes]:
    log.info("Requesting image generation...")
    try:
        safe_prompt = await app.dispatcher.run(name="assist.summarize", text=text, max_chars=220)
        return await app.dispatcher.run(name="assist.generate_image_from_summary", text_summary=safe_prompt)
    except Exception as e:
        log.error(f"Image generation task failed: {e}", exc_info=True)
        return None

async def _process_and_send_item(app: AppContext, cfg: Any, config_name: str, original_text: str, generate_image: bool):
    tasks = [_get_translated_text_task(app, original_text, cfg)]
    if generate_image:
        tasks.append(_get_image_bytes_task(app, original_text))

    if len(tasks) > 1:
        final_text, image_bytes = await asyncio.gather(*tasks)
    else:
        final_text = (await asyncio.gather(*tasks))[0]
        image_bytes = None

    if image_bytes:
        await _send_digest_with_image(app, cfg, final_text, image_bytes, config_name)
    else:
        await _send_digest_as_text(app, cfg, final_text)

async def _handle_simple_digest(app: AppContext, cfg: Any, config_name: str, rpc_results: Union[str, List[str]]):
    log.info(f"Processing single-block digest for '{config_name}'")
    original_text = "".join(rpc_results) if isinstance(rpc_results, list) else str(rpc_results or "")
    original_text = original_text.strip()
    
    if not original_text:
        log.info(f"No messages returned from digest builder for '{config_name}'.")
        return

    should_generate_image = getattr(cfg, 'generate_image', False)
    await _process_and_send_item(app, cfg, config_name, original_text, should_generate_image)

async def _handle_multi_section_digest(app: AppContext, cfg: Any, config_name: str, rpc_results: List[str]):
    log.info(f"Processing multi-section digest for '{config_name}'")
    sections_configs = list(cfg.feeds.values())

    for original_text, section_cfg in zip(rpc_results, sections_configs):
        if not original_text: continue
        should_generate_image = getattr(section_cfg, 'generate_image', False)
        await _process_and_send_item(app, cfg, config_name, original_text, should_generate_image)
        await asyncio.sleep(2)

async def execute_and_send(app: AppContext, config_name: str) -> None:
    log.info(f"Runner job started for '{config_name}'")
    try:
        cfg = getattr(app.settings, config_name)
        rpc_method_name = _get_rpc_method_name(config_name)
        
        rpc_results = await app.dispatcher.run(name=rpc_method_name, config_name=config_name)

        if hasattr(cfg, 'feeds') and isinstance(cfg.feeds, dict) and cfg.feeds:
            await _handle_multi_section_digest(app, cfg, config_name, rpc_results)
        else:
            await _handle_simple_digest(app, cfg, config_name, rpc_results)

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)