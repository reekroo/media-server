import sys
sys.path.append('/home/reekroo/scripts')
from sounds import sound_client
from src.alerters.base import Alerter
from src.earthquake_logger import get_logger

log = get_logger(__name__)

class SoundClientAlerter(Alerter):
    def trigger_alert(self, melody_name, duration):
        log.warning(f"[SoundClientAlerter] Sending alert command: play '{melody_name}' for {duration}s")
        sound_client.play_sound(melody_name, duration)