import sys
import os

# --- ВОТ РЕШЕНИЕ: Явно добавляем путь к папке со всеми общими скриптами ---
sys.path.append('/home/reekroo/scripts')
# -------------------------------------------------------------------

from src import config
from src.earthquake_logger import get_logger
from src.usgs_api import UsgsApi
from src.monitor import EarthquakeMonitor

log = get_logger(__name__)

if __name__ == "__main__":
    log.info("Starting Earthquake Monitor service...")
    
    api_client = UsgsApi()

    monitor = EarthquakeMonitor(
        api_client=api_client,
        lat=config.MY_LAT,
        lon=config.MY_LON,
        radius=config.SEARCH_RADIUS_KM,
        min_api_mag=config.MIN_API_MAGNITUDE,
        api_time_window=config.API_TIME_WINDOW_MINUTES,
        alert_levels_config=config.ALERT_LEVELS
    )

    monitor.run(config.CHECK_INTERVAL_SECONDS)
    
    log.info("Earthquake Monitor service has been shut down.")