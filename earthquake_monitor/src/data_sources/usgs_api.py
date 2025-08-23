import requests
from datetime import datetime, timezone, timedelta

import configs
from earthquake_logger import get_logger
from data_sources.base import DataSource

log = get_logger(__name__)

class UsgsApiDataSource(DataSource):
    API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def get_earthquakes(self, latitude, longitude):
        log.info("[UsgsApiDataSource] Querying USGS data source...")

        time_window = timedelta(minutes=configs.API_TIME_WINDOW_MINUTES)
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window

        params = {
            "format": "geojson",
            "latitude": latitude,
            "longitude": longitude,
            "maxradiuskm": configs.SEARCH_RADIUS_KM,
            "minmagnitude": configs.MIN_API_MAGNITUDE,
            "orderby": "time",
            "starttime": start_time_utc.isoformat(),
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            
            log.info(f"[UsgsApiDataSource] Response status code: {response.status_code}")
            response.raise_for_status()
            
            return response.json()
        
        except requests.RequestException as e:
            log.error(f"[UsgsApiDataSource] Network or API error: {e}")
            return None