import time
from src.earthquake_logger import get_logger

log = get_logger(__name__)

class EarthquakeMonitor:
    def __init__(self, api_client, earthquake_buzzer, lat, lon, radius, min_api_mag, api_time_window, alert_levels_config):
        self._api_client = api_client
        self._alarmer = earthquake_buzzer
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._min_api_mag = min_api_mag
        self._api_time_window = api_time_window
        self._alert_levels = alert_levels_config
        self._processed_event_ids = set()

    def check_and_alert(self):
        log.info("Checking for events...")
        data = self._api_client.get_significant_earthquakes(
            self._lat, self._lon, self._radius, self._min_api_mag, self._api_time_window
        )

        if not data or not data.get('features'):
            log.info("No new significant events found.")
            return

        new_events = []
        for event in data['features']:
            if event['id'] not in self._processed_event_ids:
                new_events.append(event)
        
        if not new_events:
            log.info("Found events, but they have already been processed.")
            return

        strongest_event = max(new_events, key=lambda e: e['properties'].get('mag', 0))
        
        for event in new_events:
            self._processed_event_ids.add(event['id'])

        mag = strongest_event['properties'].get('mag', 0)
        
        for level in self._alert_levels:
            if mag >= level['min_magnitude']:
                place = strongest_event['properties'].get('place', 'Unknown')
                log.warning("--- STRONGEST NEW EVENT DETECTED ---")
                log.warning(f"  Magnitude: {mag} meets threshold {level['min_magnitude']}")
                log.warning(f"  Place: {place}")
                
                actual_melody = level['melody']
                duration = level['duration']
                log.warning(f"  ALERT DURATION: {duration} seconds")
                self._alarmer.play_alarm(actual_melody, duration)
                
                break

    def run(self, interval_seconds):
        try:
            while True:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            log.info("Monitoring stopped by user.")
        finally:
            self._alarmer.close()
            log.info("Alerter resources released.")