import asyncio
from .container import build_services

class App:
    def __init__(self):
        self.services = build_services()

    async def close_resources(self):
        await self.services.http_session.close()

    async def send_notification(self, message: str, send_to: str = "default"):
        client = self.services.telegram_client
        chat_id = self.services.settings.TELEGRAM_CHAT_ID
        
        if (send_to == "telegram" or send_to == "default") and client and chat_id:
            await client.send_text(chat_id, message)
        else:
            from .channels.console.console import send_to_console
            send_to_console(message)