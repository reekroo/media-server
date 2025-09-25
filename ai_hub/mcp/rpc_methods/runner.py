import asyncio
from typing import Any, List, Optional

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
        destination=cfg.destination, 
        content=digest_text, 
        destination_topic=cfg.destination_topic
    )

async def _send_digest_with_image(app: AppContext, cfg: Any, digest_text: str, image_bytes: bytes, config_name: str) -> None:
    channel = app.channel_factory.get_channel(cfg.to)
    try:
        if len(digest_text) <= TELEGRAM_CAPTION_LIMIT:
            log.info(f"Sending photo with caption for '{config_name}'")
            await channel.send_photo(
                destination=cfg.destination, image_bytes=image_bytes,
                caption=digest_text, destination_topic=cfg.destination_topic
            )
        else:
            log.info(f"Caption for '{config_name}' is too long. Sending as separate messages.")
            photo_message = await channel.send_photo(
                destination=cfg.destination, image_bytes=image_bytes,
                caption="", destination_topic=cfg.destination_topic
            )
            await channel.send(
                destination=cfg.destination, content=digest_text,
                destination_topic=cfg.destination_topic, reply_to_message_id=photo_message.message_id
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

async def _get_image_bytes_task(app: AppContext, text: str, cfg: Any) -> Optional[bytes]:
    if not getattr(cfg, "generate_image", False):
        return None
        
    log.info("Requesting image generation...")
    try:
        safe_prompt = await app.dispatcher.run(name="assist.summarize", text=text, max_chars=220)
        return await app.dispatcher.run(name="assist.generate_image_from_summary", text_summary=safe_prompt)
    except Exception as e:
        log.error(f"Image generation task failed: {e}", exc_info=True)
        return None

async def execute_and_send(app: AppContext, config_name: str) -> None:
    log.info(f"Runner job started for '{config_name}'")
    try:
        cfg = getattr(app.settings, config_name)
        rpc_method_name = _get_rpc_method_name(config_name)
        
        digest_results: List[str] = await app.dispatcher.run(name=rpc_method_name, config_name=config_name)

        if not isinstance(digest_results, list):
            digest_results = [digest_results] if isinstance(digest_results, str) and digest_results else []
        
        if not digest_results:
            log.info(f"No messages returned from digest builder for '{config_name}'.")
            return

        for original_text in digest_results:
            tasks = [
                _get_translated_text_task(app, original_text, cfg),
                _get_image_bytes_task(app, original_text, cfg)
            ]

            final_text, image_bytes = await asyncio.gather(*tasks)

            if image_bytes:
                await _send_digest_with_image(app, cfg, final_text, image_bytes, config_name)
            else:
                await _send_digest_as_text(app, cfg, final_text)

            await asyncio.sleep(2)

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)