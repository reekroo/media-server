import time
from collections import deque
from src.earthquake_logger import get_logger

log = get_logger(__name__)

class EarthquakeMonitor:
    def __init__(self, data_sources, alerter, alert_levels_config, max_processed_events):
        self._data_sources = data_sources
        self._alerter = alerter
        self._alert_levels = alert_levels_config
        self._processed_event_ids = deque(maxlen=max_processed_events)

    def check_and_alert(self):
        log.info("[EarthquakeMonitor] Checking for events...")
        
        all_features = []
        
        for source in self._data_sources:
            data = source.get_earthquakes()
            if data and data.get('features'):
                all_features.extend(data['features'])

        if not all_features:
            log.info("[EarthquakeMonitor] No new events found from any source.")
            return

        new_events = [e for e in all_features if e.get('id') not in self._processed_event_ids]
        
        if not new_events:
            log.info("[EarthquakeMonitor] Found events, but they have already been processed.")
            return

        strongest_event = max(new_events, key=lambda e: e['properties'].get('mag', 0))
        
        for event in new_events:
            self._processed_event_ids.append(event['id'])

        mag = strongest_event['properties'].get('mag', 0)
        
        for level in self._alert_levels:
            if mag >= level['min_magnitude']:
                place = strongest_event['properties'].get('place', 'Unknown')
                log.warning("[EarthquakeMonitor] --- STRONGEST NEW EVENT DETECTED ---")
                log.warning(f"[EarthquakeMonitor] Magnitude: {mag} meets threshold {level['min_magnitude']}")
                log.warning(f"[EarthquakeMonitor] Place: {place}")
                
                melody_name = level.get('melody_name', 'ALERT_LEVEL_1') 
                duration = level.get('duration', 10)
                
                self._alerter.trigger_alert(melody_name, duration)
                
                break

    def run(self, interval_seconds):
        try:
            while True:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            log.info("[EarthquakeMonitor] Monitor service stopped by user.")
        finally:
            log.info("[EarthquakeMonitor] Monitor service has been shut down.")