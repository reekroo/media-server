import socket
import json
from .base import BaseAlerter
from earthquake_logger import get_logger
from configs import BUZZER_SOCKET

log = get_logger(__name__)

class SoundAlerter(BaseAlerter):

    def alert(self, level: int, magnitude: float, place: str):
        if not 1 <= level <= 5:
            log.warning(f"[SoundAlerter] Invalid alert level: {level}. Alert cancelled.")
            return

        melody_name = f"ALERT_LEVEL_{level}"
        command = {"melody": melody_name}
        
        log.info(f"[SoundAlerter] Sending sound command for Mag {magnitude} at '{place}': Play '{melody_name}'")
        
        client = None
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(2) 
            client.connect(BUZZER_SOCKET)
            client.sendall(json.dumps(command).encode('utf-8'))
        except Exception as e:
            log.error(f"[SoundAlerter] Could not connect to sound service: {e}")
        finally:
            if client:
                client.close()