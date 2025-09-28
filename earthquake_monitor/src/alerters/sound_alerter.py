import asyncio
import json
import logging
from .base import BaseAlerter

class SoundAlerter(BaseAlerter):
    def __init__(self, logger: logging.Logger, socket_path: str, timeout: float = 3.0):
        self._log = logger
        self._socket_path = socket_path
        self._timeout = timeout
        self._log.info(f"SoundAlerter initialized for socket path: {self._socket_path}")

    async def alert(
        self,
        level: int,
        magnitude: float,
        place: str,
        melody_name: str | None = None,
        duration: int | float | None = None,
        wait: bool = False
    ):
        if not 1 <= level <= 5:
            self._log.warning(f"[SoundAlerter] Invalid alert level: {level}. Alert cancelled.")
            return

        name = melody_name or f"ALERT_LEVEL_{level}"
        
        command = {
            "melody": name,
            "duration": float(duration or 0.0),
            "wait": bool(wait)
        }

        self._log.info(f"[SoundAlerter] Sending sound command for Mag {magnitude} at '{place}': {command}")
        
        if not await self._send_command_async(command):
            self._log.error(f"[SoundAlerter] Failed to send command to sound service at {self._socket_path}")

    async def _send_command_async(self, command: dict) -> bool:
        try:
            async with asyncio.timeout(self._timeout):
                reader, writer = await asyncio.open_unix_connection(self._socket_path)                
                writer.write(json.dumps(command).encode("utf-8"))
                await writer.drain()

                try:
                    await reader.read(16)
                finally:
                    writer.close()
                    await writer.wait_closed()
            return True
            
        except (asyncio.TimeoutError, OSError, FileNotFoundError) as e:
            self._log.error(f"[SoundAlerter] Could not connect or send to sound service: {e}")
            return False