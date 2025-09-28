import json
import logging
import os
import asyncio
from dataclasses import asdict
from typing import List

from models.earthquake_event import EarthquakeEvent

class JsonFileOutput:
    def __init__(self, logger: logging.Logger):
        self._log = logger

    def _blocking_write(self, events_as_dict: List[dict], file_path: str):
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            self._log.info(f"Created directory: {dir_name}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(events_as_dict, f, indent=4, ensure_ascii=False)

    async def write(self, events: List[EarthquakeEvent], file_path: str) -> None:
        self._log.info(f"Writing {len(events)} events to {file_path}...")
        try:
            events_as_dict = [asdict(event) for event in events]            
            await asyncio.to_thread(self._blocking_write, events_as_dict, file_path)            
            self._log.info(f"Successfully wrote data to {file_path}")

        except Exception as e:
            self._log.error(f"Failed to write to JSON file {file_path}: {e}", exc_info=True)