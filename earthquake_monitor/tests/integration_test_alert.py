from unittest.mock import MagicMock

from earthquake_monitor import EarthquakeMonitor
from alerters.sound_alerter import SoundAlerter
from models.earthquake_event import EarthquakeEvent
from earthquake_logger import setup_logger
import configs

TEST_ALERT_LEVELS_5_SEC = [
    {
        'min_magnitude': 3.0,
        'duration': 5,
        'level_id': 1,
        'melody_name': 'ALERT_LEVEL_1'
    },
]

def create_fake_earthquake(mag, event_id="physical_test_event") -> list[EarthquakeEvent]:
    return [
        EarthquakeEvent(
            event_id=event_id,
            magnitude=mag,
            place="PHYSICAL TEST LOCATION",
            latitude=0,
            longitude=0,
            timestamp=1234567890
        )
    ]

def run_physical_test():
    log = setup_logger("EarthquakePhysicalTest", configs.LOG_FILE_PATH)
    log.info("--- STARTING PHYSICAL ALERT TEST (5 seconds) ---")

    mock_data_source = MagicMock()
    mock_data_source.get_earthquakes.return_value = create_fake_earthquake(4.0)
    log.info("Fake data source created to report a magnitude 4.0 earthquake.")

    mock_location_provider = MagicMock()
    mock_location_provider.get_location.return_value = {'lat': 38.0, 'lon': 27.0}

    real_sound_alerter = SoundAlerter(logger=log, socket_path=configs.BUZZER_SOCKET)
    log.info(f"Real SoundAlerter created, will connect to {configs.BUZZER_SOCKET}.")

    monitor = EarthquakeMonitor(
        data_sources=[mock_data_source],
        alerters=[real_sound_alerter],
        location_providers=[mock_location_provider],
        alert_levels_config=TEST_ALERT_LEVELS_5_SEC, 
        logger=log,
        max_processed_events=10
    )
    log.info("EarthquakeMonitor instance created with test components.")

    log.info(">>> TRIGGERING check_and_alert(). Listen for a 5-second buzzer! <<<")
    monitor.check_and_alert()

    log.info("--- PHYSICAL ALERT TEST COMPLETE ---")

if __name__ == "__main__":
    run_physical_test()