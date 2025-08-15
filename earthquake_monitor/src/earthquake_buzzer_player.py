import time

from src.earthquake_logger import get_logger

log = get_logger(__name__)

class EarthquakeBuzzerPlayer:
    def __init__(self, buzzer_player):
        self._player = buzzer_player

    def play_alarm(self, melody, duration_seconds):
        if self._player.is_playing:
            log.warning("Buzzer is already busy. Skipping new alarm.")
            return
        
        log.info(f"Playing alarm for {duration_seconds} seconds.")
        start_time = time.time()
        try:
            while time.time() - start_time < duration_seconds:
                self._player.play(melody)
                if time.time() - start_time >= duration_seconds:
                    break
                time.sleep(0.1)
        finally:
            self._player.is_playing = False
            log.info("Alarm finished.")

    def close(self):
        self._player.close()
