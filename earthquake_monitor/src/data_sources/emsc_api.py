import requests
from datetime import datetime, timezone, timedelta

import configs
from earthquake_logger import get_logger
from data_sources.base import DataSource

log = get_logger(__name__)

class EmscApiDataSource(DataSource):
    API_URL = "https://www.seismicportal.eu/fdsnws/event/1/query"

    def get_earthquakes(self, latitude, longitude):
        log.info("[EmscApiDataSource] Querying EMSC data source...")

        time_window = timedelta(minutes=configs.API_TIME_WINDOW_MINUTES)
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window        
        radius_deg = configs.SEARCH_RADIUS_KM / 111.0

        params = {
            "format": "json",
            "latitude": latitude,
            "longitude": longitude,
            "maxradius": f"{radius_deg:.2f}",
            "minmagnitude": configs.MIN_API_MAGNITUDE,
            "orderby": "time",
            "start": start_time_utc.isoformat(),
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            if response.status_code == 204:
                log.info("[EmscApiDataSource] Received 204 No Content, no new events.")
                return None 

            log.info(f"[EmscApiDataSource] Response status code: {response.status_code}")
            response.raise_for_status()

            return response.json()
        
        except requests.RequestException as e:
            log.error(f"[EmscApiDataSource] Network or API error: {e}")
            return None