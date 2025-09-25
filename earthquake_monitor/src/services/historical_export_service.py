# services/historical_export_service.py
import logging
from datetime import datetime, timedelta, timezone
from typing import List

from data_sources.base import BaseApiDataSource
from locations.base import ILocationProvider
from models.earthquake_event import EarthquakeEvent
from outputs.json_file_output import JsonFileOutput

class HistoricalExportService:
    def __init__(self,
                 data_sources: List[BaseApiDataSource],
                 location_providers: List[ILocationProvider],
                 output: JsonFileOutput,
                 logger: logging.Logger,
                 output_path: str,
                 fetch_days: int):
        self._data_sources = data_sources
        self._location_providers = location_providers
        self._output = output
        self._log = logger
        self._output_path = output_path
        self._fetch_days = fetch_days


    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = provider.get_location()
            if location:
                return location
        self._log.error("[HistoricalDataFetcher] Failed to get location from all available providers.")
        return None

    def execute_export(self) -> None:
        self._log.info(f"Historical export: Fetching data for the last {self._fetch_days} days...")
        current_location = self._get_current_location()
        if not current_location:
            self._log.error("Historical export: Could not determine location, skipping fetch.")
            return
            
        start_time = datetime.now(timezone.utc) - timedelta(days=self._fetch_days)

        all_events: List[EarthquakeEvent] = []
        for source in self._data_sources:
            events = source.get_earthquakes(current_location['lat'], current_location['lon'], start_time=start_time)
            all_events.extend(events)

        if not all_events:
            self._log.info("Historical export: No events fetched, skipping file write.")
            return

        unique_events = list({event.event_id: event for event in all_events}.values())
        self._log.info(f"Historical export: Fetched {len(unique_events)} unique events.")
        
        self._output.write(unique_events, self._output_path)