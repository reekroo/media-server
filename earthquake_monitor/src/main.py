#!/usr/bin/env python3

import configs
from earthquake_logger import get_logger
from earthquake_monitor import EarthquakeMonitor
from data_sources.emsc_api import EmscApiDataSource
from data_sources.isc_api import IscApiDataSource
from data_sources.usgs_api import UsgsApiDataSource
from alerters.sound_alerter import SoundAlerter

log = get_logger(__name__)

def main():
    log.info("[Earthquake Main] Initializing Earthquake Monitor service...")
    
    data_sources = [
        UsgsApiDataSource(),
        EmscApiDataSource(),
        IscApiDataSource()
    ]
    
    alerters = [
        SoundAlerter(),
    ]

    monitor = EarthquakeMonitor(
        data_sources=data_sources,
        alerters=alerters,
        alert_levels_config=configs.ALERT_LEVELS,
        max_processed_events=configs.MAX_PROCESSED_EVENTS_MEMORY
    )

    monitor.run(configs.CHECK_INTERVAL_SECONDS)
    
    log.info("[Earthquake Main] Earthquake Monitor service has been shut down.")

if __name__ == "__main__":
    main()