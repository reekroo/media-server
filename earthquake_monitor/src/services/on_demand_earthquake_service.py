import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

from data_sources.base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class OnDemandEarthquakeService:
    def __init__(self, data_sources: List[BaseApiDataSource], logger: logging.Logger):
        self._data_sources = data_sources
        self._log = logger

    async def get_earthquakes_for_coords(self, lat: float, lon: float, days: int = 1) -> List[EarthquakeEvent]:
        self._log.info(f"On-demand: Fetching earthquake data for coords ({lat}, {lon}) for last {days} day(s)...")
        start_time = datetime.now(timezone.utc) - timedelta(days=days)

        tasks = [
            source.get_earthquakes(lat, lon, start_time=start_time)
            for source in self._data_sources
        ]
        results_from_sources = await asyncio.gather(*tasks, return_exceptions=True)

        all_events: List[EarthquakeEvent] = []
        for i, result in enumerate(results_from_sources):
            if isinstance(result, Exception):
                source_name = self._data_sources[i].name
                self._log.error(f"On-demand: Task for source '{source_name}' failed with an exception: {result}")
            elif result:
                all_events.extend(result)

        if not all_events:
            self._log.info("On-demand: No events found from any source.")
            return []

        unique_events = list({event.event_id: event for event in all_events}.values())
        sorted_events = sorted(unique_events, key=lambda e: e.timestamp, reverse=True)
        
        self._log.info(f"On-demand: Found {len(sorted_events)} unique events after deduplication.")
        return sorted_events