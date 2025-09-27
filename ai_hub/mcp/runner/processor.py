import asyncio
from typing import Optional

from core.logging import setup_logger, LOG_FILE_PATH
from mcp.context import AppContext
from .models import DeliveryItem

log = setup_logger(__name__, LOG_FILE_PATH)

class ContentProcessor:
    def __init__(self, app: AppContext):
        self.app = app

    async def _get_translated_text(self, text: str, target_lang: Optional[str]) -> str:
        if not target_lang or target_lang.lower() == self.app.settings.DEFAULT_LANGUAGE.lower():
            return text
        log.info(f"Translating digest to '{target_lang}'...")
        try:
            return await self.app.dispatcher.run("assist.translate", text=text, target_lang=target_lang)
        except Exception as e:
            log.error(f"Translation task failed: {e}", exc_info=True)
            return text

    async def _get_image_bytes(self, text: str) -> Optional[bytes]:
        log.info("Requesting image generation...")
        try:
            safe_prompt = await self.app.dispatcher.run(name="assist.summarize", text=text, max_chars=220)
            return await self.app.dispatcher.run(name="assist.generate_image_from_summary", text_summary=safe_prompt)
        except Exception as e:
            log.error(f"Image generation task failed: {e}", exc_info=True)
            return None

    async def process(self, item: DeliveryItem) -> tuple[str, Optional[bytes]]:
        tasks = [self._get_translated_text(item.original_text, item.target_lang)]
        if item.generate_image:
            tasks.append(self._get_image_bytes(item.original_text))

        results = await asyncio.gather(*tasks)
        final_text = results[0]
        image_bytes = results[1] if len(results) > 1 else None
        return final_text, image_bytes