import socket
import json
import logging
from .base import BaseAlerter

class SoundAlerter(BaseAlerter):
    def __init__(self, logger: logging.Logger, socket_path: str, timeout: float = 3.0):
        self._log = logger
        self._socket_path = socket_path
        self._timeout = timeout
        self._log.info(f"SoundAlerter initialized for socket path: {self._socket_path}")

    def alert(
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

        self._log.info(
            f"[SoundAlerter] Sending sound command for Mag {magnitude} at '{place}': {command}"
        )
        
        if not self._send_command(command):
            self._log.error(f"[SoundAlerter] Failed to send command to sound service at {self._socket_path}")

    def _send_command(self, command: dict) -> bool:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(self._timeout)
                client.connect(self._socket_path)
                client.sendall(json.dumps(command).encode("utf-8"))
                
                try:
                    client.recv(16)
                except (socket.timeout, ConnectionResetError):
                    pass
            return True
            
        except (socket.error, FileNotFoundError, socket.timeout) as e:
            self._log.error(f"[SoundAlerter] Could not connect or send to sound service: {e}")
            return False