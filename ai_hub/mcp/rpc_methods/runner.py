import logging
from mcp.context import AppContext
from mcp.dispatcher import Dispatcher

log = logging.getLogger(__name__)

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
        # 1. Генерируем контент на дефолтном языке
        digest_text = await dispatcher.run(name=rpc_method_name, config_name=config_name)

        # 2. Решаем, нужен ли перевод
        cfg = getattr(app.settings, config_name)
        target_lang = getattr(cfg, "destination_language", None)
        
        if target_lang and target_lang.lower() != app.settings.DEFAULT_LANG.lower():
            log.info(f"Translating digest '{config_name}' to '{target_lang}'...")
            digest_text = await dispatcher.run(
                name="assist.translate", text=digest_text, target_lang=target_lang
            )

        # 3. Отправляем финальный результат
        if cfg and cfg.destination and digest_text and "no output" not in digest_text:
            log.info(f"Sending digest '{config_name}' to {cfg.destination}")
            channel = app.channel_factory.get_channel(cfg.to)
            await channel.send(destination=cfg.destination, content=digest_text)
        else:
            log.warning(f"Did not send digest for '{config_name}': no destination or no content.")

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)