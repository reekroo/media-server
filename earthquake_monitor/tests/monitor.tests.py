import unittest
from unittest.mock import MagicMock
from earthquake_monitor.src.earthquake_monitor import EarthquakeMonitor

MOCK_ALERT_LEVELS = [
    {
        'min_magnitude': 6.0,
        'duration': 180,
        'melody': ['L4_MELODY']
    },
    {
        'min_magnitude': 4.5,
        'duration': 60,
        'melody': ['L3_MELODY']
    },
]

MOCK_MIN_API_MAG = 4.5

def create_mock_api_response(mag, event_id="test_event_1"):
    return {
        "features": [
            {
                "id": event_id,
                "properties": { "mag": mag, "place": "Test Location" }
            }
        ]
    }

class TestEarthquakeMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_api_client = MagicMock()
        self.mock_alarm_controller = MagicMock()
        
        self.monitor = EarthquakeMonitor(
            api_client=self.mock_api_client,
            alarm_controller=self.mock_alarm_controller,
            lat=0, lon=0, radius=100,
            min_api_mag=MOCK_MIN_API_MAG,
            alert_levels_config=MOCK_ALERT_LEVELS 
        )

    def test_triggers_correct_level_for_high_magnitude(self):
        self.mock_api_client.get_significant_earthquakes.return_value = create_mock_api_response(6.5)
        self.monitor.check_and_alert()
        self.mock_alarm_controller.play_alarm.assert_called_once_with(
            ['L4_MELODY'], 180
        )

    def test_triggers_correct_level_for_medium_magnitude(self):
        self.mock_api_client.get_significant_earthquakes.return_value = create_mock_api_response(5.0)
        self.monitor.check_and_alert()
        self.mock_alarm_controller.play_alarm.assert_called_once_with(
            ['L3_MELODY'], 60
        )

    def test_no_alert_below_threshold(self):
        self.mock_api_client.get_significant_earthquakes.return_value = create_mock_api_response(4.0)
        self.monitor.check_and_alert()
        self.mock_alarm_controller.play_alarm.assert_not_called()

    def test_no_alert_for_processed_event(self):
        self.mock_api_client.get_significant_earthquakes.return_value = create_mock_api_response(5.0)
        self.monitor.check_and_alert()
        self.monitor.check_and_alert()
        self.mock_alarm_controller.play_alarm.assert_called_once()

if __name__ == '__main__':
    unittest.main()