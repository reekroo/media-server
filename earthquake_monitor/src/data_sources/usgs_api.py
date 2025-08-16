import requests
from datetime import datetime, timezone, timedelta
from src import configs
from src.earthquake_logger import get_logger
from src.data_sources.base import DataSource

log = get_logger(__name__)

class UsgsApiDataSource(DataSource):
    API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def get_earthquakes(self):
        log.info("[UsgsApiDataSource] Querying USGS data source...")

        time_window = timedelta(minutes=configs.API_TIME_WINDOW_MINUTES)
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window

        params = {
            "format": "geojson",
            "latitude": configs.MY_LAT,
            "longitude": configs.MY_LON,
            "maxradiuskm": configs.SEARCH_RADIUS_KM,
            "minmagnitude": configs.MIN_API_MAGNITUDE,
            "orderby": "time",
            "starttime": start_time_utc.isoformat(),
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            log.info(f"[UsgsApiDataSource] Response status code: {response.status_code}")
            return response.json()
        except requests.RequestException as e:
            log.error(f"[UsgsApiDataSource] Network or API error: {e}")
            return None