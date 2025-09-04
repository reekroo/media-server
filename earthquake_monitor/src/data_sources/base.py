from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

from models.earthquake_event import EarthquakeEvent
from utils.http_client import HttpClient

class BaseApiDataSource(ABC):
    def __init__(self, http_client: HttpClient, logger: logging.Logger, config: Dict[str, Any]):
        self._http_client = http_client
        self._log = logger
        self._config = config
        self.name = self.__class__.__name__

    def get_earthquakes(self, latitude: float, longitude: float) -> List[EarthquakeEvent]:
        self._log.info(f"Querying {self.name} data source...")
        
        url, params, headers = self._build_request_params(latitude, longitude)
        
        try:
            response = self._http_client.get(url, params=params, headers=headers)
            if response.status_code == 204:
                self._log.info(f"[{self.name}] Received 204 No Content, no new events.")
                return []
            
            events = self._parse_response(response.text)
            self._log.info(f"[{self.name}] Successfully parsed response, found {len(events)} event(s).")
            return events
        
        except Exception as e:
            self._log.error(f"[{self.name}] Failed to fetch or parse data: {e}")
            return []

    @abstractmethod
    def _build_request_params(self, latitude: float, longitude: float) -> (str, Dict, Dict):
        pass

    @abstractmethod
    def _parse_response(self, response_text: str) -> List[EarthquakeEvent]:
        pass

    def _get_start_time_iso(self) -> str:
        time_window = timedelta(minutes=self._config.get('API_TIME_WINDOW_MINUTES', 15))
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window
        return start_time_utc.isoformat()