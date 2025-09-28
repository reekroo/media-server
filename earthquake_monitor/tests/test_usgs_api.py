import unittest
import logging
import json
from unittest.mock import MagicMock

from data_sources.usgs_api import UsgsApiDataSource
from models.earthquake_event import EarthquakeEvent

SAMPLE_USGS_RESPONSE = """
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 5.5,
                "place": "12km N of Anytown, CA",
                "time": 1678886400000
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-122.7, 38.4, 10.0]
            },
            "id": "us12345"
        }
    ]
}
"""

INCOMPLETE_USGS_RESPONSE = """
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": { "place": "Incomplete data" },
            "geometry": null,
            "id": "us_incomplete"
        }
    ]
}
"""

class TestUsgsApiDataSource(unittest.TestCase):

    def setUp(self):
        self.mock_http_client = MagicMock()
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.config = {
            'SEARCH_RADIUS_KM': 250,
            'MIN_API_MAGNITUDE': 3.0,
            'API_TIME_WINDOW_MINUTES': 15
        }
        self.data_source = UsgsApiDataSource(
            http_client=self.mock_http_client,
            logger=self.mock_logger,
            config=self.config
        )

    def test_parse_response_success(self):
        data = json.loads(SAMPLE_USGS_RESPONSE)
        events = self.data_source._parse_response(data)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertIsInstance(event, EarthquakeEvent)
        self.assertEqual(event.event_id, "us12345")
        self.assertEqual(event.magnitude, 5.5)
        self.assertEqual(event.place, "12km N of Anytown, CA")
        self.assertEqual(event.longitude, -122.7)
        self.assertEqual(event.latitude, 38.4)
        self.assertEqual(event.timestamp, 1678886400)

    def test_parse_response_handles_incomplete_data(self):
        data = json.loads(INCOMPLETE_USGS_RESPONSE)
        events = self.data_source._parse_response(data)
        self.assertEqual(len(events), 0)

    def test_parse_response_handles_empty_json(self):
        events = self.data_source._parse_response({'features': []})
        self.assertEqual(len(events), 0)