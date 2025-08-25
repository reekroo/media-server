#!/usr/bin/env python3

import time
from collections import deque
from typing import List
from locations.base import ILocationProvider
from data_sources.base import DataSource
from alerters.base import BaseAlerter
from earthquake_logger import get_logger

log = get_logger(__name__)

class EarthquakeMonitor:
    def __init__(self, 
                 data_sources: List[DataSource], 
                 location_providers: List[ILocationProvider] = None,
                 alerters: List[BaseAlerter] = None,
                 alert_levels_config=None, 
                 max_processed_events: int = 100):
        self._data_sources = data_sources or []
        self._location_providers = location_providers or []
        self._alerters = alerters or []
        self._alert_levels = alert_levels_config or []
        self._processed_event_ids = deque(maxlen=max_processed_events)
        log.info("[EarthquakeMonitor] initialized.")

    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = provider.get_location()
            if location:
                return location
        log.error("Failed to get location from all available providers.")
        return None

    def check_and_alert(self) -> None:
        log.info("[EarthquakeMonitor] Checking for events...")

        current_location = self._get_current_location() if self._location_providers else {"lat": 0.0, "lon": 0.0}
        if not current_location:
            log.error("Could not determine location, skipping weather check.")
            return

        all_features = []
        for source in self._data_sources:
            try:
                data = source.get_earthquakes(current_location['lat'], current_location['lon'])
                if data and data.get('features'):
                    all_features.extend(data['features'])
            except Exception as e:
                log.error(f"[EarthquakeMonitor] Failed to get data from {type(source).__name__}: {e}")

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
        place = strongest_event['properties'].get('place', 'Unknown')

        for level_cfg in self._alert_levels:
            if mag >= level_cfg.get('min_magnitude', 0):
                level_id = level_cfg.get('level_id', 1)
                melody_name = level_cfg.get('melody_name') or f"ALERT_LEVEL_{level_id}"
                duration = level_cfg.get('duration', 0)

                log.warning("--- STRONGEST NEW EVENT DETECTED ---")
                log.warning(f"Magnitude: {mag} (Threshold: {level_cfg.get('min_magnitude')})")
                log.warning(f"Place: {place}")

                for alerter in self._alerters:
                    alerter.alert(
                        level=level_id,
                        magnitude=mag,
                        place=place,
                        melody_name=melody_name,
                        duration=duration
                    )
                break

    def run(self, interval_seconds: int) -> None:
        try:
            while True:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            log.info("[EarthquakeMonitor] Monitor service stopped by user.")
        finally:
            log.info("[EarthquakeMonitor] Monitor service has been shut down.")
