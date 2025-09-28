import logging
from collections import deque
from typing import List
import asyncio

from alerters.base import BaseAlerter
from locations.base import ILocationProvider
from data_sources.base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class RealtimeMonitorService:
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
        self._log.info("RealtimeMonitorService initialized.")

    async def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = await provider.get_location()
            if location:
                return location
        self._log.error("Failed to get location from all available providers.")
        return None

    async def execute_check(self) -> None:
        self._log.info("Realtime check: Checking for new earthquake events...")

        current_location = await self._get_current_location()
        if not current_location:
            self._log.error("Realtime check: Could not determine location, skipping check cycle.")
            return

        tasks = [
            source.get_earthquakes(current_location['lat'], current_location['lon'])
            for source in self._data_sources
        ]
        results_from_sources = await asyncio.gather(*tasks, return_exceptions=True)

        all_events: List[EarthquakeEvent] = []
        for i, result in enumerate(results_from_sources):
            if isinstance(result, Exception):
                source_name = self._data_sources[i].name
                self._log.error(f"Realtime check: Source '{source_name}' failed: {result}")
            elif result:
                all_events.extend(result)
            
        if not all_events:
            self._log.info("Realtime check: No events found from any source.")
            return
            
        unique_events = {event.event_id: event for event in all_events}        
        new_events = [event for event in unique_events.values() if event.event_id not in self._processed_event_ids]

        if not new_events:
            self._log.info("Realtime check: Found events, but they have already been processed.")
            return

        strongest_event = max(new_events, key=lambda e: e.magnitude)
        
        for event in new_events:
            self._processed_event_ids.append(event.event_id)

        await self._trigger_alert_for_event(strongest_event)

    async def _trigger_alert_for_event(self, event: EarthquakeEvent) -> None:
        for level_cfg in self._alert_levels:
            if event.magnitude >= level_cfg['min_magnitude']:
                self._log.warning("--- STRONGEST NEW EVENT DETECTED ---")
                self._log.warning(f"Magnitude: {event.magnitude} (Threshold: {level_cfg['min_magnitude']})")
                self._log.warning(f"Place: {event.place}")

                alert_tasks = []
                for alerter in self._alerters:
                    task = alerter.alert(
                        level=level_cfg['level_id'],
                        magnitude=event.magnitude,
                        place=event.place,
                        melody_name=level_cfg['melody_name'],
                        duration=level_cfg['duration']
                    )
                    alert_tasks.append(task)
                
                await asyncio.gather(*alert_tasks)
                
                return