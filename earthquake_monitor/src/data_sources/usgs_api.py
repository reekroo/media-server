import json
from typing import List, Dict

from .base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class UsgsApiDataSource(BaseApiDataSource):
    API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def _build_request_params(self, latitude: float, longitude: float, start_time_iso: str) -> (str, Dict, Dict):
        params = {
            "format": "geojson",
            "latitude": latitude,
            "longitude": longitude,
            "maxradiuskm": self._config.get('SEARCH_RADIUS_KM'),
            "minmagnitude": self._config.get('MIN_API_MAGNITUDE'),
            "orderby": "time",
            "starttime": start_time_iso,
        }
        return self.API_URL, params, {}

    def _parse_response(self, response_text: str) -> List[EarthquakeEvent]:
        if not response_text or not response_text.strip().startswith('{'):
            self._log.warning(f"[{self.name}] Received empty or non-JSON response, skipping. Content: '{response_text[:200]}'")
            return []
        try:
            data = json.loads(response_text)
            events = []
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                mag = props.get('mag')
                time_ms = props.get('time')

                if mag is None or time_ms is None or not geom.get('coordinates'):
                    continue
                
                events.append(EarthquakeEvent(
                    event_id=feature.get('id'),
                    magnitude=float(mag),
                    place=props.get('place', 'Unknown'),
                    longitude=geom['coordinates'][0],
                    latitude=geom['coordinates'][1],
                    timestamp=int(time_ms) // 1000
                ))
            return events
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self._log.error(f"[{self.name}] Error parsing JSON response: {e}. Response text: '{response_text[:500]}'")
            return []