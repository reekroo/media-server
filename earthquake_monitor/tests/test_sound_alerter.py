import unittest
from unittest.mock import MagicMock

from src.earthquake_monitor import EarthquakeMonitor
from src.alerters.base import BaseAlerter

MOCK_ALERT_LEVELS = [
    {'min_magnitude': 6.0, 'level_id': 4, 'melody_name': 'ALERT_LEVEL_4', 'duration': 180},
    {'min_magnitude': 4.5, 'level_id': 3, 'melody_name': 'ALERT_LEVEL_3', 'duration': 60},
]

def create_mock_api_response(mag, event_id="test_event_1"):
    return {
        "features": [
            {"id": event_id, "properties": {"mag": mag, "place": "Test Location"}}
        ]
    }

class TestEarthquakeMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_data_source = MagicMock()
        self.mock_alerter = MagicMock(spec=BaseAlerter)

        self.monitor = EarthquakeMonitor(
            data_sources=[self.mock_data_source],
            alerters=[self.mock_alerter],
            alert_levels_config=MOCK_ALERT_LEVELS,
            max_processed_events=100
        )

    def test_triggers_correct_level_for_high_magnitude(self):
        # Arrange
        self.mock_data_source.get_earthquakes.return_value = create_mock_api_response(6.5)
        
        # Act
        self.monitor.check_and_alert()

        # Assert
        self.mock_alerter.alert.assert_called_once_with(
            level=4,
            magnitude=6.5,
            place="Test Location"
        )

    def test_triggers_correct_level_for_medium_magnitude(self):
        # Arrange
        self.mock_data_source.get_earthquakes.return_value = create_mock_api_response(5.0)
        
        # Act
        self.monitor.check_and_alert()

        # Assert
        self.mock_alerter.alert.assert_called_once_with(
            level=3,
            magnitude=5.0,
            place="Test Location"
        )

    def test_no_alert_below_threshold(self):
        # Arrange
        self.mock_data_source.get_earthquakes.return_value = create_mock_api_response(4.0)
        
        # Act
        self.monitor.check_and_alert()
        
        # Assert
        self.mock_alerter.alert.assert_not_called()

    def test_no_alert_for_processed_event(self):
        # Arrange
        self.mock_data_source.get_earthquakes.return_value = create_mock_api_response(5.0, event_id="processed_event")
        
        # Act
        self.monitor.check_and_alert()
        self.monitor.check_and_alert()
        
        # Assert
        self.mock_alerter.alert.assert_called_once()