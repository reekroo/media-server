import unittest
import logging
import json
from unittest.mock import MagicMock

from data_sources.emsc_api import EmscApiDataSource
from models.earthquake_event import EarthquakeEvent

SAMPLE_EMSC_RESPONSE_TIME_AS_STRING = """
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 4.2,
                "place": "GREECE",
                "time": "1678881234567" 
            },
            "geometry": { "type": "Point", "coordinates": [25.5, 39.1] },
            "id": "emsc123"
        }
    ]
}
"""

SAMPLE_EMSC_RESPONSE_ISO_TIME = """
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 3.5,
                "place": "WESTERN TURKEY",
                "time": "2025-09-04T03:58:21.9Z"
            },
            "geometry": { "type": "Point", "coordinates": [28.1837, 39.1957] },
            "id": "20250904_0000058"
        }
    ]
}
"""

class TestEmscApiDataSource(unittest.TestCase):

    def setUp(self):
        self.mock_http_client = MagicMock()
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.config = {
            'SEARCH_RADIUS_KM': 250,
            'MIN_API_MAGNITUDE': 3.0,
            'API_TIME_WINDOW_MINUTES': 15
        }
        self.data_source = EmscApiDataSource(
            http_client=self.mock_http_client,
            logger=self.mock_logger,
            config=self.config
        )

    def test_parse_response_with_string_time(self):
        data = json.loads(SAMPLE_EMSC_RESPONSE_TIME_AS_STRING)
        events = self.data_source._parse_response(data)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertIsInstance(event, EarthquakeEvent)
        self.assertEqual(event.event_id, "emsc123")
        self.assertEqual(event.timestamp, 1678881234)

    def test_parse_response_with_iso_time(self):
        from datetime import datetime, timezone
        data = json.loads(SAMPLE_EMSC_RESPONSE_ISO_TIME)
        events = self.data_source._parse_response(data)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.event_id, "20250904_0000058")

        result_dt = datetime.fromtimestamp(event.timestamp, tz=timezone.utc)
        self.assertEqual(result_dt.year, 2025)
        self.assertEqual(result_dt.month, 9)
        self.assertEqual(result_dt.day, 4)
        self.assertEqual(result_dt.hour, 3)
        self.assertEqual(result_dt.minute, 58)
        self.assertEqual(result_dt.second, 21)

    def test_parse_response_handles_malformed_event(self):
        malformed_response = """
        {
            "features": [
                {"id": "good_event", "properties": {"mag": 5.0, "place": "Good Place", "time": "1678886400000"}, "geometry": {"coordinates": [1, 2]}},
                {"id": "bad_event", "properties": {"mag": "invalid_mag", "place": "Bad Place", "time": "not_a_time"}, "geometry": {"coordinates": [3, 4]}}
            ]
        }
        """
        data = json.loads(malformed_response)
        events = self.data_source._parse_response(data)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_id, "good_event")