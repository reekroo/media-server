from __future__ import annotations

from typing import Optional

from .channels.telegram_send.telegram_send import TelegramClient

class App:
    def __init__(self, services: Optional[object] = None):
        if services is None:
            from .container import build_services
            services = build_services()
        self.services = services
        self._tg_client: Optional[TelegramClient] = None

    @property
    def tg_client(self) -> TelegramClient:
        if self._tg_client is None:
            bot_token = self.services.settings.TELEGRAM_BOT_TOKEN
            self._tg_client = TelegramClient(bot_token)
        return self._tg_client

    async def send_notification(self, message: str, send_to: str = "telegram") -> None:
        if send_to == "telegram":
            chat_id = self.services.settings.TELEGRAM_CHAT_ID
            await self.tg_client.send_text(chat_id, message)
        else:
            raise NotImplementedError(f"Unsupported destination: {send_to}")

    async def close_resources(self) -> None:
        try:
            if self._tg_client is not None:
                await self._tg_client.close()
        except Exception:
            pass
