import time
from unittest.mock import MagicMock

from earthquake_monitor import EarthquakeMonitor
from alerters.sound_alerter import SoundAlerter
import configs
from earthquake_logger import get_logger

log = get_logger("EarthquakePhysicalTest")

def create_fake_earthquake(mag, event_id="fake_event_1"):
    return {
        "features": [
            {"id": event_id, "properties": {"mag": mag, "place": "PHYSICAL TEST LOCATION"}}
        ]
    }

def run_physical_test():
    log.info("--- STARTING PHYSICAL ALERT TEST ---")

    mock_data_source = MagicMock()
    mock_data_source.get_earthquakes.return_value = create_fake_earthquake(7.5)
    log.info("Fake data source created with magnitude 7.5 earthquake.")

    real_sound_alerter = SoundAlerter()
    log.info("Real SoundAlerter created.")

    monitor = EarthquakeMonitor(
        data_sources=[mock_data_source],
        alerters=[real_sound_alerter],
        alert_levels_config=configs.ALERT_LEVELS,
        max_processed_events=100
    )
    log.info("EarthquakeMonitor instance created with test components.")

    log.info(">>> TRIGGERING CHECK_AND_ALERT(). Listen for the buzzer! <<<")
    monitor.check_and_alert()

    log.info("--- PHYSICAL ALERT TEST COMPLETE ---")

if __name__ == "__main__":
    run_physical_test()