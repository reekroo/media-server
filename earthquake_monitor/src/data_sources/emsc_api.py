import json
from datetime import datetime
from typing import List, Dict, Any

from .base import BaseApiDataSource, ApiResponseType
from models.earthquake_event import EarthquakeEvent

class EmscApiDataSource(BaseApiDataSource):
    API_URL = "https://www.seismicportal.eu/fdsnws/event/1/query"
    RESPONSE_TYPE = ApiResponseType.JSON

    def _build_request_params(self, latitude: float, longitude: float, start_time_iso: str) -> (str, Dict, Dict):
        radius_km = self._config.get('SEARCH_RADIUS_KM', 250)
        radius_deg = radius_km / 111.0
        
        params = {
            "format": "json",
            "latitude": latitude,
            "longitude": longitude,
            "maxradius": f"{radius_deg:.2f}",
            "minmagnitude": self._config.get('MIN_API_MAGNITUDE'),
            "orderby": "time",
            "starttime": start_time_iso, 
        }
        return self.API_URL, params, {}
    
    def _parse_response(self, data: Dict[str, Any]) -> list[EarthquakeEvent]:
        try:
            events = []
            for feature in data.get('features', []):
                try:
                    props = feature.get('properties', {})
                    geom = feature.get('geometry', {})

                    if props.get('mag') is None or not geom or not geom.get('coordinates'):
                        continue
                    
                    time_value = props.get('time')
                    if time_value is None:
                        continue

                    timestamp_sec = 0
                    try:
                        timestamp_sec = int(time_value) // 1000
                    except ValueError:
                        aware_dt_object = datetime.fromisoformat(time_value)
                        timestamp_sec = int(aware_dt_object.timestamp())

                    events.append(EarthquakeEvent(
                        event_id=feature.get('id'),
                        magnitude=float(props['mag']),
                        place=props.get('place', 'Unknown'),
                        longitude=geom['coordinates'][0],
                        latitude=geom['coordinates'][1],
                        timestamp=timestamp_sec
                    ))
                except (ValueError, TypeError) as e:
                    self._log.warning(f"[{self.name}] Skipping an event due to data conversion error: {e}. Data: {feature}")
                    continue
            return events
        except (KeyError, IndexError) as e:
            self._log.error(f"[{self.name}] Error parsing JSON object: {e}. Data snippet: '{str(data)[:500]}'")
            return []