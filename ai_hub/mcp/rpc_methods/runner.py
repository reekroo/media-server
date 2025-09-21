from typing import Any

from mcp.context import AppContext
from mcp.dispatcher import Dispatcher
from core.logging import setup_logger, LOG_FILE_PATH
from core.constants.news import UNIVERSAL_NEWS_DIGESTS

log = setup_logger(__name__, LOG_FILE_PATH)

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace('_digest','').replace('_brief','')
    return f"{target_builder}.{short_func_name}"

async def _translate_digest_if_needed(app: AppContext, digest_text: str, target_lang: str | None) -> str:
    if not target_lang or target_lang.lower() == app.settings.DEFAULT_LANGUAGE.lower():
        return digest_text

    log.info(f"Translating digest to '{target_lang}'...")
    try:
        translated_text = await app.dispatcher.run(
            name="assist.translate", text=digest_text, target_lang=target_lang
        )
        return translated_text
    except Exception as e:
        log.error(f"Translation failed: {e}", exc_info=True)
        return digest_text

async def _send_digest_as_text(app: AppContext, cfg: Any, digest_text: str) -> None:
    channel = app.channel_factory.get_channel(cfg.to)
    await channel.send(
        destination=cfg.destination, 
        content=digest_text, 
        destination_topic=cfg.destination_topic
    )

async def _send_digest_with_image(app: AppContext, cfg: Any, digest_text: str) -> None:
    try:
        log.info(f"Requesting image generation for '{cfg.config_name}'...")
        safe_prompt = await app.dispatcher.run(name="assist.summarize", text=digest_text, max_chars=220)
        image_bytes = await app.dispatcher.run(name="assist.generate_image_from_summary", text_summary=safe_prompt)
        
        channel = app.channel_factory.get_channel(cfg.to)
        await channel.send_photo(
            destination=cfg.destination,
            image_bytes=image_bytes,
            caption=digest_text,
            destination_topic=cfg.destination_topic
        )
    except Exception as e:
        log.error(f"Failed to generate or send image for '{cfg.config_name}': {e}", exc_info=True)
        error_message = f"⚠️ _Image generation failed._\n\n{digest_text}"
        await _send_digest_as_text(app, cfg, error_message)

async def execute_and_send(app: AppContext, config_name: str) -> None:
    log.info(f"Runner job started for '{config_name}'")
    
    try:
        rpc_method_name = _get_rpc_method_name(config_name)
        digest_results = await app.dispatcher.run(name=rpc_method_name, config_name=config_name)

        if isinstance(digest_results, str):
            digest_results = [digest_results]

        cfg = getattr(app.settings, config_name)
        cfg.config_name = config_name 

        for digest_text in digest_results:
            if not digest_text or "no output" in digest_text:
                log.warning(f"Did not send digest for '{config_name}': empty content.")
                continue

            final_text = await _translate_digest_if_needed(app, digest_text, getattr(cfg, "destination_language", None))
            
            if getattr(cfg, "generate_image", False):
                await _send_digest_with_image(app, cfg, final_text)
            else:
                await _send_digest_as_text(app, cfg, final_text)

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)