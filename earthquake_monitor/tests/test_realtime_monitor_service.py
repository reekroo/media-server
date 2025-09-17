import logging
from unittest.mock import MagicMock, ANY

import configs
from services.realtime_monitor_service import RealtimeMonitorService
from models.earthquake_event import EarthquakeEvent

logger = logging.getLogger('test_logger')

def test_execute_check_triggers_alert_for_new_strong_event():
    strong_event = EarthquakeEvent(
        event_id="test001", magnitude=5.5, place="Test Land",
        latitude=10, longitude=20, timestamp=1234567890
    )
    
    mock_data_source = MagicMock()
    mock_data_source.get_earthquakes.return_value = [strong_event]

    mock_location_provider = MagicMock()
    mock_location_provider.get_location.return_value = {"lat": 10.0, "lon": 20.0}
    
    mock_alerter = MagicMock()

    service = RealtimeMonitorService(
        data_sources=[mock_data_source],
        location_providers=[mock_location_provider],
        alerters=[mock_alerter],
        alert_levels_config=configs.ALERT_LEVELS,
        logger=logger,
        max_processed_events=10
    )
    service.execute_check()

    mock_location_provider.get_location.assert_called_once()
    mock_data_source.get_earthquakes.assert_called_once()
    
    mock_alerter.alert.assert_called_once_with(
        level=3,
        magnitude=5.5,
        place="Test Land",
        melody_name='ALERT_LEVEL_3',
        duration=45
    )

def test_execute_check_does_not_alert_for_processed_event():
    processed_event = EarthquakeEvent(event_id="test002", magnitude=6.0, place="Old Land", latitude=10, longitude=20, timestamp=123)
    mock_data_source = MagicMock()
    mock_data_source.get_earthquakes.return_value = [processed_event]
    mock_location_provider = MagicMock()
    mock_location_provider.get_location.return_value = {"lat": 10.0, "lon": 20.0}
    mock_alerter = MagicMock()

    service = RealtimeMonitorService(
        data_sources=[mock_data_source], location_providers=[mock_location_provider],
        alerters=[mock_alerter], alert_levels_config=configs.ALERT_LEVELS, logger=logger
    )
    
    service.execute_check()
    service.execute_check()

    mock_alerter.alert.assert_called_once()