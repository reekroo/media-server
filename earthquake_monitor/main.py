import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src import config
from src.earthquake_logger import get_logger
from src.earthquake_buzzer_player import EarthquakeBuzzerPlayer
from src.usgs_api import UsgsApi
from src.monitor import EarthquakeMonitor
from scripts.sounds.libs.buzzer_player import BuzzerPlayer

log = get_logger(__name__)

if __name__ == "__main__":
    log.info("Starting Earthquake Monitor service...")
    
    base_player = BuzzerPlayer(pin=config.BUZZER_PIN)
    earthquake_buzzer = EarthquakeBuzzerPlayer(base_player)

    api_client = UsgsApi()

    monitor = EarthquakeMonitor(
        api_client=api_client,
        earthquake_buzzer=earthquake_buzzer,
        lat=config.MY_LAT,
        lon=config.MY_LON,
        radius=config.SEARCH_RADIUS_KM,
        min_api_mag=config.MIN_API_MAGNITUDE,
        api_time_window=config.API_TIME_WINDOW_MINUTES,
        alert_levels_config=config.ALERT_LEVELS
    )

    monitor.run(config.CHECK_INTERVAL_SECONDS)
    
    log.info("Earthquake Monitor service has been shut down.")