import logging
from mcp.context import AppContext
from mcp.dispatcher import Dispatcher

log = logging.getLogger(__name__)

# Список "универсальных" дайджестов, которые обрабатываются одним методом
UNIVERSAL_NEWS_DIGESTS = {
    "news", "news_by", "news_tr", "gaming", "entertainment"
}

async def execute_and_send(app: AppContext, config_name: str) -> None:
    """
    Умный обработчик для runner-а.
    Сначала генерирует контент, вызывая правильный RPC-метод,
    а затем отправляет результат в канал из конфига.
    """
    log.info(f"Runner job started for '{config_name}'")
    
    dispatcher: Dispatcher = app.dispatcher
    
    # --- УМНАЯ ЛОГИКА ОПРЕДЕЛЕНИЯ МЕТОДА ---
    target_builder_config = config_name
    if config_name in UNIVERSAL_NEWS_DIGESTS:
        # Если это один из "новостных" дайджестов, мы должны вызвать универсальный метод 'news.build'
        target_builder_config = "news"

    # Формируем имя RPC-метода по соглашению
    base_func_name = "build_brief" if target_builder_config == "daily" else "build_digest"
    rpc_method_name = f"{target_builder_config}.{base_func_name.replace('_digest','').replace('_brief','')}"
    # --- КОНЕЦ УМНОЙ ЛОГИКИ ---

    try:
        log.info(f"Dispatching to '{rpc_method_name}' with config '{config_name}'")
        # Вызываем метод-генератор контента
        digest_text = await dispatcher.run(name=rpc_method_name, config_name=config_name)
    except KeyError:
        log.error(f"MCP Dispatcher Error: Method '{rpc_method_name}' not found!")
        return
    except Exception as e:
        log.error(f"Error executing digest builder '{rpc_method_name}': {e}", exc_info=True)
        return

    # Отправляем результат
    cfg = getattr(app.settings, config_name)
    if cfg and cfg.destination and digest_text and "no output" not in digest_text:
        log.info(f"Sending digest '{config_name}' to {cfg.destination}")
        channel = app.channel_factory.get_channel(cfg.to)
        await channel.send(destination=cfg.destination, content=digest_text)
    else:
        log.warning(f"Did not send digest for '{config_name}': no destination or no content.")