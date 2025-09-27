import asyncio
from typing import Any, List

from core.logging import setup_logger, LOG_FILE_PATH
from core.config_models import FeedBasedConfig, MessageTargetConfig
from mcp.context import AppContext
from .models import DeliveryItem
from .processor import ContentProcessor
from .sender import TelegramSender

log = setup_logger(__name__, LOG_FILE_PATH)

def _prepare_delivery_items(cfg: MessageTargetConfig, rpc_results: Any) -> List[DeliveryItem]:
    items_to_deliver: List[DeliveryItem] = []
    target_lang = getattr(cfg, "destination_language", None)

    if isinstance(cfg, FeedBasedConfig):
        log.info(f"Preparing multi-section digest...")
        sections_configs = list(cfg.feeds.values())
        for text, section_cfg in zip(rpc_results, sections_configs):
            if text and text.strip():
                items_to_deliver.append(DeliveryItem(
                    original_text=text,
                    generate_image=getattr(section_cfg, 'generate_image', False),
                    target_lang=target_lang
                ))
    else:
        log.info(f"Preparing single-block digest...")
        text = "".join(rpc_results) if isinstance(rpc_results, list) else str(rpc_results or "")
        if text and text.strip():
            items_to_deliver.append(DeliveryItem(
                original_text=text,
                generate_image=getattr(cfg, 'generate_image', False),
                target_lang=target_lang
            ))
    return items_to_deliver

async def _process_and_deliver(app: AppContext, cfg: MessageTargetConfig, config_name: str, rpc_results: Any):
    items = _prepare_delivery_items(cfg, rpc_results)
    if not items:
        log.info(f"No messages to deliver for '{config_name}'.")
        return

    processor = ContentProcessor(app)
    sender = TelegramSender(app.channel_factory.get_channel(cfg.to), cfg, config_name)
    
    for i, item in enumerate(items):
        final_text, image_bytes = await processor.process(item)
        await sender.send(final_text, image_bytes)
        
        if i < len(items) - 1:
            await asyncio.sleep(2)

async def run_job(app: AppContext, config_name: str) -> None:
    log.info(f"Runner job started for '{config_name}'")
    try:
        cfg = getattr(app.settings, config_name)
        if not cfg or not getattr(cfg, 'enabled', False):
            log.warning(f"Digest '{config_name}' is disabled or not configured.")
            return

        rpc_results = await app.dispatcher.run(name=cfg.rpc_method, config_name=config_name)
        await _process_and_deliver(app, cfg, config_name, rpc_results)

    except Exception as e:
        log.error(f"Failed to execute runner job for '{config_name}': {e}", exc_info=True)