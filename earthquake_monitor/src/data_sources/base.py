import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

from models.earthquake_event import EarthquakeEvent
from utils.http_client import HttpClient

class BaseApiDataSource(ABC):
    API_URL: str

    def __init__(self, http_client: HttpClient, logger: logging.Logger, config: Dict[str, Any]):
        self._http_client = http_client
        self._log = logger
        self._config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def _build_request_params(self, latitude: float, longitude: float, start_time_iso: str) -> (str, Dict, Dict):
        pass

    @abstractmethod
    def _parse_response(self, response_text: str) -> List[EarthquakeEvent]:
        pass

    def get_earthquakes(self, latitude: float, longitude: float, start_time: datetime = None) -> List[EarthquakeEvent]:
        if start_time is None:
            time_window_minutes = self._config.get('API_TIME_WINDOW_MINUTES', 15)
            start_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)

        start_time_iso = start_time.isoformat().replace('+00:00', 'Z')
        url, params, headers = self._build_request_params(latitude, longitude, start_time_iso)

        try:
            response = self._http_client.get(url, params=params, headers=headers)
            
            if response and hasattr(response, 'text'):
                return self._parse_response(response.text)
            
            self._log.warning(f"[{self.name}] Received an empty or invalid response.")
            return []

        except Exception as e:
            self._log.error(f"[{self.name}] Failed to fetch or parse data: {e}", exc_info=True)
            return []