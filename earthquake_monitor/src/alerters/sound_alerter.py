import socket
import json
from .base import BaseAlerter
from earthquake_logger import get_logger

log = get_logger(__name__)

SOCKET_FILE = "/tmp/buzzer.sock"

class SoundAlerter(BaseAlerter):
    
    def alert(self, level: int, magnitude: float, location: str):
        if not 1 <= level <= 5:
            log.warning(f"[SoundAlerter] Invalid alert level: {level}. Must be 1-5.")
            return

        melody_name = f"ALERT_LEVEL_{level}"
        command = {"melody": melody_name}
        
        log.info(f"[SoundAlerter] Sending sound command for Mag {magnitude} at {location}: Play '{melody_name}'")
        
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(2) 
            client.connect(SOCKET_FILE)
            client.sendall(json.dumps(command).encode('utf-8'))

            log.info(f"[SoundAlerter] Command sent successfully.")
        except Exception as e:
            log.error(f"[SoundAlerter] Could not connect to sound service: {e}")
        finally:
            if 'client' in locals() and client:
                client.close()