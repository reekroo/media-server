import logging
import enum
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from models.earthquake_event import EarthquakeEvent
from utils.http_client import HttpClient

class ApiResponseType(enum.Enum):
    JSON = 'json'
    TEXT = 'text'

class BaseApiDataSource(ABC):
    RESPONSE_TYPE: ApiResponseType = ApiResponseType.JSON

    def __init__(self, http_client: HttpClient, logger: logging.Logger, config: Dict[str, Any]):
        self._http_client = http_client
        self._log = logger
        self._config = config
        self.name = self.__class__.__name__
        
    @abstractmethod
    def _build_request_params(self, latitude: float, longitude: float, start_time_iso: str) -> (str, Dict, Dict):
        pass

    @abstractmethod
    def _parse_response(self, response_data: Any) -> List[EarthquakeEvent]:
        pass
        
    async def get_earthquakes(self, latitude: float, longitude: float, start_time: Optional[datetime] = None) -> List[EarthquakeEvent]:
        time_window_minutes = self._config.get('API_TIME_WINDOW_MINUTES', 15)
        
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)

        start_time_iso = start_time.isoformat().replace('+00:00', 'Z')
        url, params, headers = self._build_request_params(latitude, longitude, start_time_iso)

        try:
            self._log.debug(f"[{self.name}] Fetching data from {url}")
            
            response_data = None
            if self.RESPONSE_TYPE == ApiResponseType.JSON:
                response_data = await self._http_client.get_json(url, params=params, headers=headers)
            else:
                response_data = await self._http_client.get_text(url, params=params, headers=headers)

            if response_data:
                return self._parse_response(response_data)
            
            return []
        except Exception as e:
            self._log.error(f"[{self.name}] An unexpected error occurred: {e}", exc_info=True)
            return []