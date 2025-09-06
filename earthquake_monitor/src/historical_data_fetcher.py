import logging
from datetime import datetime, timedelta, timezone
from typing import List

from data_sources.base import BaseApiDataSource
from locations.base import ILocationProvider
from models.earthquake_event import EarthquakeEvent

class HistoricalDataFetcher:
    def __init__(self,
                 data_sources: List[BaseApiDataSource],
                 location_providers: List[ILocationProvider],
                 logger: logging.Logger):
        self._data_sources = data_sources
        self._location_providers = location_providers
        self._log = logger

    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = provider.get_location()
            if location:
                return location
        self._log.error("[HistoricalDataFetcher] Failed to get location from all available providers.")
        return None

    def fetch_last_n_days(self, days: int) -> List[EarthquakeEvent]:
        self._log.info(f"Fetching historical earthquake data for the last {days} days...")
        
        current_location = self._get_current_location()
        if not current_location:
            self._log.error("[HistoricalDataFetcher] Could not determine location, skipping fetch.")
            return []
            
        start_time = datetime.now(timezone.utc) - timedelta(days=days)

        all_events: List[EarthquakeEvent] = []
        for source in self._data_sources:
            events = source.get_earthquakes(current_location['lat'], current_location['lon'], start_time=start_time)
            all_events.extend(events)

        unique_events = list({event.event_id: event for event in all_events}.values())
        self._log.info(f"Fetched {len(unique_events)} unique historical events.")
        
        return unique_events