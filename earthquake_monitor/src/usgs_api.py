import requests
from datetime import datetime, timezone, timedelta
from src import config

from src.earthquake_logger import get_logger

log = get_logger(__name__)

class UsgsApi:
    API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def get_significant_earthquakes(self, lat, lon, radius_km, min_mag, time_window_minutes):
        time_window = timedelta(minutes=time_window_minutes)
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window

        params = {
            "format": "geojson",
            "latitude": lat,
            "longitude": lon,
            "maxradiuskm": radius_km,
            "minmagnitude": min_mag,
            "orderby": "time",
            "starttime": start_time_utc.isoformat(),
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            log.error(f"Network or API error: {e}")
            return None