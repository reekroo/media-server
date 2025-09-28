import logging
import asyncio
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

    async def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = await provider.get_location()
            if location:
                return location
        self._log.error("[HistoricalDataFetcher] Failed to get location from all available providers.")
        return None

    async def execute_export(self) -> None:
        self._log.info(f"Historical export: Fetching data for the last {self._fetch_days} days...")
        current_location = await self._get_current_location()
        if not current_location:
            self._log.error("Historical export: Could not determine location, skipping fetch.")
            return
            
        start_time = datetime.now(timezone.utc) - timedelta(days=self._fetch_days)

        tasks = [
            source.get_earthquakes(current_location['lat'], current_location['lon'], start_time=start_time)
            for source in self._data_sources
        ]
        results_from_sources = await asyncio.gather(*tasks, return_exceptions=True)

        all_events: List[EarthquakeEvent] = []
        for i, result in enumerate(results_from_sources):
            if isinstance(result, Exception):
                source_name = self._data_sources[i].name
                self._log.error(f"Historical export: Source '{source_name}' failed: {result}")
            elif result:
                all_events.extend(result)

        if not all_events:
            self._log.info("Historical export: No events fetched, skipping file write.")
            return

        unique_events = list({event.event_id: event for event in all_events}.values())
        self._log.info(f"Historical export: Fetched {len(unique_events)} unique events.")
        
        await self._output.write(unique_events, self._output_path)