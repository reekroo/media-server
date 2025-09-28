import unittest
import logging
from unittest.mock import MagicMock

from data_sources.isc_api import IscApiDataSource
from models.earthquake_event import EarthquakeEvent

SAMPLE_ISC_RESPONSE_XML = """
<q:quakeml xmlns:q="http://quakeml.org/xmlns/quakeml/1.2" xmlns:bed="http://quakeml.org/xmlns/bed/1.2">
  <bed:eventParameters>
    <bed:event q:publicID="isc123">
      <bed:description>
        <bed:text>CENTRAL TURKEY</bed:text>
      </bed:description>
      <bed:origin>
        <bed:latitude><bed:value>38.01</bed:value></bed:latitude>
        <bed:longitude><bed:value>37.22</bed:value></bed:longitude>
        <bed:time><bed:value>2025-09-04T12:34:56.789Z</bed:value></bed:time>
      </bed:origin>
      <bed:magnitude>
        <bed:mag><bed:value>6.7</bed:value></bed:mag>
      </bed:magnitude>
    </bed:event>
  </bed:eventParameters>
</q:quakeml>
"""

EMPTY_ISC_RESPONSE_XML = """
<q:quakeml xmlns:q="http://quakeml.org/xmlns/quakeml/1.2" xmlns:bed="http://quakeml.org/xmlns/bed/1.2">
  <bed:eventParameters/>
</q:quakeml>
"""

class TestIscApiDataSource(unittest.TestCase):

    def setUp(self):
        self.mock_http_client = MagicMock()
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.config = {
            'SEARCH_RADIUS_KM': 250,
            'MIN_API_MAGNITUDE': 3.0,
            'API_TIME_WINDOW_MINUTES': 15
        }
        self.data_source = IscApiDataSource(
            http_client=self.mock_http_client,
            logger=self.mock_logger,
            config=self.config
        )

    def test_parse_xml_response_success(self):
        from datetime import datetime, timezone

        events = self.data_source._parse_response(SAMPLE_ISC_RESPONSE_XML)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.event_id, "isc123")
        self.assertEqual(event.magnitude, 6.7)

        result_dt = datetime.fromtimestamp(event.timestamp, tz=timezone.utc)

        self.assertEqual(result_dt.year, 2025)
        self.assertEqual(result_dt.month, 9)
        self.assertEqual(result_dt.day, 4)
        self.assertEqual(result_dt.hour, 12)
        self.assertEqual(result_dt.minute, 34)
        self.assertEqual(result_dt.second, 56)

    def test_parse_xml_handles_empty_response(self):
        events = self.data_source._parse_response(EMPTY_ISC_RESPONSE_XML)
        self.assertEqual(len(events), 0)

    def test_parse_xml_handles_invalid_xml(self):
        events = self.data_source._parse_response("<not>valid</xml>")
        self.assertEqual(len(events), 0)