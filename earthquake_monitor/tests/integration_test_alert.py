import asyncio
from unittest.mock import MagicMock, AsyncMock

from services.realtime_monitor_service import RealtimeMonitorService
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

async def run_physical_test():
    log = setup_logger("EarthquakePhysicalTest", configs.LOG_FILE_PATH)
    log.info("--- STARTING PHYSICAL ALERT TEST (5 seconds) ---")

    mock_data_source = MagicMock()
    mock_data_source.get_earthquakes = AsyncMock(return_value=create_fake_earthquake(4.0))
    log.info("Fake data source created to report a magnitude 4.0 earthquake.")

    mock_location_provider = MagicMock()
    mock_location_provider.get_location = AsyncMock(return_value={'lat': 38.0, 'lon': 27.0})

    real_sound_alerter = SoundAlerter(logger=log, socket_path=configs.BUZZER_SOCKET)
    log.info(f"Real SoundAlerter created, will connect to {configs.BUZZER_SOCKET}.")

    monitor_service = RealtimeMonitorService(
        data_sources=[mock_data_source],
        alerters=[real_sound_alerter],
        location_providers=[mock_location_provider],
        alert_levels_config=TEST_ALERT_LEVELS_5_SEC, 
        logger=log,
        max_processed_events=10
    )
    log.info("RealtimeMonitorService instance created with test components.")

    log.info(">>> TRIGGERING execute_check(). Listen for a 5-second buzzer! <<<")
    await monitor_service.execute_check()

    log.info("--- PHYSICAL ALERT TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_physical_test())