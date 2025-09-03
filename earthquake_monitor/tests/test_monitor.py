import unittest
import logging
from unittest.mock import MagicMock

from earthquake_monitor import EarthquakeMonitor
from models.earthquake_event import EarthquakeEvent

MOCK_ALERT_LEVELS = [
    {'min_magnitude': 6.0, 'level_id': 4, 'melody_name': 'ALERT_LEVEL_4', 'duration': 180},
    {'min_magnitude': 4.5, 'level_id': 3, 'melody_name': 'ALERT_LEVEL_3', 'duration': 60},
]

def create_mock_events(mag, event_id="test_event_1") -> list[EarthquakeEvent]:
    return [
        EarthquakeEvent(
            event_id=event_id,
            magnitude=mag,
            place="Test Location",
            latitude=0,
            longitude=0,
            timestamp=1234567890
        )
    ]

class TestEarthquakeMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_data_source = MagicMock()
        self.mock_alerter = MagicMock()
        self.mock_location_provider = MagicMock()
        self.mock_logger = MagicMock(spec=logging.Logger)

        self.monitor = EarthquakeMonitor(
            data_sources=[self.mock_data_source],
            alerters=[self.mock_alerter],
            location_providers=[self.mock_location_provider],
            alert_levels_config=MOCK_ALERT_LEVELS,
            logger=self.mock_logger,
            max_processed_events=100
        )
       
        self.mock_location_provider.get_location.return_value = {'lat': 38.0, 'lon': 27.0}

    def test_triggers_correct_level_for_high_magnitude(self):
        self.mock_data_source.get_earthquakes.return_value = create_mock_events(6.5)
        self.monitor.check_and_alert()
        
        self.mock_alerter.alert.assert_called_once_with(
            level=4,
            magnitude=6.5,
            place="Test Location",
            melody_name="ALERT_LEVEL_4",
            duration=180
        )

    def test_triggers_correct_level_for_medium_magnitude(self):
        self.mock_data_source.get_earthquakes.return_value = create_mock_events(5.0)
        self.monitor.check_and_alert()
        
        self.mock_alerter.alert.assert_called_once_with(
            level=3,
            magnitude=5.0,
            place="Test Location",
            melody_name="ALERT_LEVEL_3",
            duration=60
        )

    def test_no_alert_below_threshold(self):
        self.mock_data_source.get_earthquakes.return_value = create_mock_events(4.0)
        self.monitor.check_and_alert()
        
        self.mock_alerter.alert.assert_not_called()

    def test_no_alert_for_processed_event(self):
        self.mock_data_source.get_earthquakes.return_value = create_mock_events(5.0, event_id="processed_event")
        self.monitor.check_and_alert()
        
        self.monitor.check_and_alert()
        
        self.mock_alerter.alert.assert_called_once()