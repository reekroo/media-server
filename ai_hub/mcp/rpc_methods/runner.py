from mcp.context import AppContext
from mcp.dispatcher import Dispatcher
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

UNIVERSAL_NEWS_DIGESTS = {"news", "news_by", "news_tr", "gaming", "entertainment"}

def _get_rpc_method_name(config_name: str) -> str:
    target_builder = "news" if config_name in UNIVERSAL_NEWS_DIGESTS else config_name
    base_func_name = "build_brief" if target_builder == "daily" else "build_digest"
    short_func_name = base_func_name.replace('_digest','').replace('_brief','')
    return f"{target_builder}.{short_func_name}"

async def execute_and_send(app: AppContext, config_name: str) -> None:
    log.info(f"Runner job started for '{config_name}'")
    dispatcher: Dispatcher = app.dispatcher
    rpc_method_name = _get_rpc_method_name(config_name)

    try:
        digest_results = await dispatcher.run(name=rpc_method_name, config_name=config_name)

        if isinstance(digest_results, str):
            digest_results = [digest_results]

        cfg = getattr(app.settings, config_name)
        target_lang = getattr(cfg, "destination_language", None)
        should_generate_image = getattr(cfg, "generate_image", False)

        for digest_text in digest_results:
            if not digest_text or "no output" in digest_text:
                log.warning(f"Did not send digest for '{config_name}': empty content.")
                continue

            if target_lang and target_lang.lower() != app.settings.DEFAULT_LANG.lower():
                log.info(f"Translating digest '{config_name}' to '{target_lang}'...")
                try:
                    digest_text = await dispatcher.run(
                        name="assist.translate", text=digest_text, target_lang=target_lang
                    )
                except Exception as e:
                    log.error(f"Translation failed for '{config_name}': {e}", exc_info=True)

            image_sent = False
            if should_generate_image:
                log.info(f"Requesting image generation for '{config_name}'...")
                try:
                    safe_prompt = await dispatcher.run(name="assist.summarize", text=digest_text, max_chars=220)
                    image_bytes = await dispatcher.run(name="assist.generate_image_from_summary", text_summary=safe_prompt)
                    
                    channel = app.channel_factory.get_channel(cfg.to)
                    await channel.send_photo(
                        destination=cfg.destination,
                        image_bytes=image_bytes,
                        caption=digest_text,
                        destination_topic=cfg.destination_topic
                    )
                    image_sent = True
                except Exception as e:
                    log.error(f"Failed to generate or send image for '{config_name}': {e}", exc_info=True)

            if not image_sent:
                channel = app.channel_factory.get_channel(cfg.to)
                await channel.send(
                    destination=cfg.destination, 
                    content=digest_text, 
                    destination_topic=cfg.destination_topic
                )

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)