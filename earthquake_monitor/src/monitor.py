import time
from collections import deque
from src.earthquake_logger import get_logger
from sounds import sound_client

log = get_logger(__name__)

class EarthquakeMonitor:
    def __init__(self, api_client, lat, lon, radius, min_api_mag, api_time_window, alert_levels_config, max_processed_events):
        self._api_client = api_client
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._min_api_mag = min_api_mag
        self._api_time_window = api_time_window
        self._alert_levels = alert_levels_config
        self._processed_event_ids = deque(maxlen=max_processed_events)

    def check_and_alert(self):
        log.info("Checking for events...")
        data = self._api_client.get_significant_earthquakes(
            self._lat, self._lon, self._radius, self._min_api_mag, self._api_time_window
        )

        if not data or not data.get('features'):
            log.info("No new significant events found.")
            return

        new_events = [e for e in data.get('features', []) if e.get('id') not in self._processed_event_ids]
        
        if not new_events:
            log.info("Found events, but they have already been processed.")
            return

        strongest_event = max(new_events, key=lambda e: e['properties'].get('mag', 0))
        
        for event in new_events:
            self._processed_event_ids.append(event['id'])

        mag = strongest_event['properties'].get('mag', 0)
        
        for level in self._alert_levels:
            if mag >= level['min_magnitude']:
                place = strongest_event['properties'].get('place', 'Unknown')
                log.warning("--- STRONGEST NEW EVENT DETECTED ---")
                log.warning(f"  Magnitude: {mag} meets threshold {level['min_magnitude']}")
                log.warning(f"  Place: {place}")
                
                melody_name = level.get('melody_name', 'ALERT_LEVEL_1') 
                duration = level.get('duration', 10)
                log.warning(f"  Sending alert command: play '{melody_name}' for {duration}s")
                sound_client.play_sound(melody_name, duration)
                
                break

    def run(self, interval_seconds):
        try:
            while True:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            log.info("Monitoring stopped by user.")
        finally:
            log.info("Earthquake Monitor service has been shut down.")