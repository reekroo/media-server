import json
from typing import List, Dict

from .base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class EmscApiDataSource(BaseApiDataSource):
    API_URL = "https://www.seismicportal.eu/fdsnws/event/1/query"

    def _build_request_params(self, latitude: float, longitude: float) -> (str, Dict, Dict):
        radius_km = self._config.get('SEARCH_RADIUS_KM', 250)
        radius_deg = radius_km / 111.0
        
        params = {
            "format": "json",
            "latitude": latitude,
            "longitude": longitude,
            "maxradius": f"{radius_deg:.2f}",
            "minmagnitude": self._config.get('MIN_API_MAGNITUDE'),
            "orderby": "time",
            "start": self._get_start_time_iso(),
        }
        return self.API_URL, params, {}

    def _parse_response(self, response_text: str) -> List[EarthquakeEvent]:
        try:
            data = json.loads(response_text)
            events = []
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                if props.get('mag') is None or not geom or not geom.get('coordinates'):
                    continue
                
                timestamp_ms = props.get('time', 0)
                
                events.append(EarthquakeEvent(
                    event_id=feature.get('id'),
                    magnitude=float(props['mag']),
                    place=props.get('place', 'Unknown'),
                    longitude=geom['coordinates'][0],
                    latitude=geom['coordinates'][1],
                    timestamp=timestamp_ms // 1000
                ))
            return events
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self._log.error(f"[{self.name}] Error parsing JSON response: {e}")
            return []