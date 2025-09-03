import json
from typing import List, Dict
from typing import List

from .base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class UsgsApiDataSource(BaseApiDataSource):
    API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def _build_request_params(self, latitude: float, longitude: float) -> (str, Dict, Dict):
        params = {
            "format": "geojson",
            "latitude": latitude,
            "longitude": longitude,
            "maxradiuskm": self._config.get('SEARCH_RADIUS_KM'),
            "minmagnitude": self._config.get('MIN_API_MAGNITUDE'),
            "orderby": "time",
            "starttime": self._get_start_time_iso(),
        }
        return self.API_URL, params, {}

    def _parse_response(self, response_text: str) -> List[EarthquakeEvent]:
        try:
            data = json.loads(response_text)
            events = []
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                if props.get('mag') is None or not geom.get('coordinates'):
                    continue
                
                events.append(EarthquakeEvent(
                    event_id=feature.get('id'),
                    magnitude=float(props['mag']),
                    place=props.get('place', 'Unknown'),
                    longitude=geom['coordinates'][0],
                    latitude=geom['coordinates'][1],
                    timestamp=props.get('time', 0) // 1000
                ))
            return events
        except (json.JSONDecodeError, KeyError) as e:
            self._log.error(f"[{self.name}] Error parsing JSON response: {e}")
            return []