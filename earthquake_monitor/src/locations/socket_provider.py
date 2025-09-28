import asyncio
import json
import logging

from .base import ILocationProvider

class SocketLocationProvider(ILocationProvider):
    def __init__(self, logger: logging.Logger, socket_path: str, timeout: int = 5):
        self._log = logger
        self._socket_path = socket_path
        self._timeout = timeout

    async def get_location(self) -> dict | None:
        self._log.info(f"Attempting to get location from socket: {self._socket_path}...")
        
        try:
            async with asyncio.timeout(self._timeout):
                reader, writer = await asyncio.open_unix_connection(self._socket_path)                
                data = await reader.read(1024)                
                writer.close()
                await writer.wait_closed()
                
                if data:
                    location = json.loads(data.decode('utf-8'))
                    self._log.info("Successfully received location from service: %s", location)
                    return location
            return None
            
        except (asyncio.TimeoutError, FileNotFoundError, json.JSONDecodeError, OSError) as e:
            self._log.warning(f"Failed to get location from service socket: {e}")
            return None