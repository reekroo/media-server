import time
import logging
from collections import deque
from typing import List

from alerters.base import BaseAlerter
from locations.base import ILocationProvider
from data_sources.base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class EarthquakeMonitor:
    def __init__(self,
                 data_sources: List[BaseApiDataSource],
                 location_providers: List[ILocationProvider],
                 alerters: List[BaseAlerter],
                 alert_levels_config: List[dict],
                 logger: logging.Logger,
                 max_processed_events: int = 100):
        self._data_sources = data_sources
        self._location_providers = location_providers
        self._alerters = alerters
        self._alert_levels = sorted(alert_levels_config, key=lambda x: x['min_magnitude'], reverse=True)
        self._processed_event_ids = deque(maxlen=max_processed_events)
        self._log = logger
        self._log.info("EarthquakeMonitor initialized.")

    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = provider.get_location()
            if location:
                return location
        self._log.error("Failed to get location from all available providers.")
        return None

    def check_and_alert(self) -> None:
        self._log.info("Checking for new earthquake events...")

        current_location = self._get_current_location()
        if not current_location:
            self._log.error("Could not determine location, skipping check cycle.")
            return

        all_events: List[EarthquakeEvent] = []
        for source in self._data_sources:
            events = source.get_earthquakes(current_location['lat'], current_location['lon'])
            all_events.extend(events)
            
        if not all_events:
            self._log.info("No events found from any source.")
            return
            
        unique_events = {event.event_id: event for event in all_events}        
        new_events = [event for event in unique_events.values() if event.event_id not in self._processed_event_ids]

        if not new_events:
            self._log.info("Found events, but they have already been processed.")
            return

        strongest_event = max(new_events, key=lambda e: e.magnitude)
        
        for event in new_events:
            self._processed_event_ids.append(event.event_id)

        self._trigger_alert_for_event(strongest_event)

    def _trigger_alert_for_event(self, event: EarthquakeEvent) -> None:
        for level_cfg in self._alert_levels:
            if event.magnitude >= level_cfg['min_magnitude']:
                self._log.warning("--- STRONGEST NEW EVENT DETECTED ---")
                self._log.warning(f"Magnitude: {event.magnitude} (Threshold: {level_cfg['min_magnitude']})")
                self._log.warning(f"Place: {event.place}")

                for alerter in self._alerters:
                    alerter.alert(
                        level=level_cfg['level_id'],
                        magnitude=event.magnitude,
                        place=event.place,
                        melody_name=level_cfg['melody_name'],
                        duration=level_cfg['duration']
                    )
                break

    def run(self, interval_seconds: int) -> None:
        try:
            while True:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self._log.info("Monitor service stopped by user.")
        finally:
            self._log.info("Monitor service has been shut down.")