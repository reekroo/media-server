import sys
import os

from src import configs
from src.earthquake_logger import get_logger
from src.earthquake_monitor import EarthquakeMonitor
from src.data_sources.emsc_api import EmscApiDataSource
from src.data_sources.isc_api import IscApiDataSource
from src.data_sources.usgs_api import UsgsApiDataSource
from src.alerters.sound_client_alerter import SoundClientAlerter

log = get_logger(__name__)

if __name__ == "__main__":
    log.info("[Earthquake Main] Starting Earthquake Monitor service...")
    
    data_sources = [
        UsgsApiDataSource(),
        EmscApiDataSource(),
        IscApiDataSource()
    ]
    
    alerter = SoundClientAlerter()

    monitor = EarthquakeMonitor(
        data_sources=data_sources,
        alerter=alerter,
        alert_levels_config=configs.ALERT_LEVELS,
        max_processed_events=configs.MAX_PROCESSED_EVENTS_MEMORY
    )

    monitor.run(configs.CHECK_INTERVAL_SECONDS)
    
    log.info("[Earthquake Main] Earthquake Monitor service has been shut down.")