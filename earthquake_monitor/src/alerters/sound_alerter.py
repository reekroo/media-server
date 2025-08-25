import socket
import json
from .base import BaseAlerter
from earthquake_logger import get_logger
from configs import BUZZER_SOCKET  # оставляю твой путь к сокету

log = get_logger(__name__)

class SoundAlerter(BaseAlerter):
    def alert(
        self,
        level: int,
        magnitude: float,
        place: str,
        melody_name: str | None = None,
        duration: int | float | None = None,
        wait: bool = False,
        timeout: float = 3.0,
    ):
        if not 1 <= level <= 5:
            log.warning(f"[SoundAlerter] Invalid alert level: {level}. Alert cancelled.")
            return

        name = melody_name or f"ALERT_LEVEL_{level}"
        dur = float(duration or 0.0)

        command = {
            "melody": name,
            "duration": dur,
            "wait": bool(wait)
        }

        log.info(
            f"[SoundAlerter] Sending sound command for Mag {magnitude} at '{place}': "
            f"Play '{name}' (duration={dur}, wait={wait})"
        )

        client: socket.socket | None = None
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(timeout)
            client.connect(BUZZER_SOCKET)
            client.sendall(json.dumps(command).encode("utf-8"))

            try:
                _ = client.recv(16)
            except Exception:
                pass

        except Exception as e:
            log.error(f"[SoundAlerter] Could not connect to sound service: {e}")
        
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
