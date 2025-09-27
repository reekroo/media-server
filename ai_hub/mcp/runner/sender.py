from typing import Any, Optional

from core.logging import setup_logger, LOG_FILE_PATH
from core.config_models import MessageTargetConfig

log = setup_logger(__name__, LOG_FILE_PATH)
TELEGRAM_CAPTION_LIMIT = 1024

class TelegramSender:
    def __init__(self, channel: Any, cfg: MessageTargetConfig, config_name: str):
        self.channel = channel
        self.cfg = cfg
        self.config_name = config_name

    async def send(self, text: str, image_bytes: Optional[bytes] = None):
        if image_bytes:
            await self._send_with_image(text, image_bytes)
        else:
            await self._send_as_text(text)

    async def _send_as_text(self, text: str):
        await self.channel.send(
            destination=self.cfg.destination_group,
            content=text,
            destination_topic=self.cfg.destination_topic
        )

    async def _send_with_image(self, text: str, image_bytes: bytes):
        try:
            if len(text) <= TELEGRAM_CAPTION_LIMIT:
                await self.channel.send_photo(
                    destination=self.cfg.destination_group, image_bytes=image_bytes,
                    caption=text, destination_topic=self.cfg.destination_topic
                )
            else:
                photo_message = await self.channel.send_photo(
                    destination=self.cfg.destination_group, image_bytes=image_bytes,
                    caption="", destination_topic=self.cfg.destination_topic
                )
                reply_id = photo_message.message_id if photo_message else None
                await self.channel.send(
                    destination=self.cfg.destination_group, content=text,
                    destination_topic=self.cfg.destination_topic, reply_to_message_id=reply_id
                )
        except Exception as e:
            log.error(f"Failed to send photo for '{self.config_name}': {e}", exc_info=True)
            error_message = f"⚠️ _Image was generated, but failed to send._\n\n{text}"
            await self._send_as_text(error_message)