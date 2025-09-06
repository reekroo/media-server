import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict

from .base import BaseApiDataSource
from models.earthquake_event import EarthquakeEvent

class IscApiDataSource(BaseApiDataSource):
    API_URL = "https://www.isc.ac.uk/fdsnws/event/1/query"

    def _build_request_params(self, latitude: float, longitude: float, start_time_iso: str) -> (str, Dict, Dict):
        radius_km = self._config.get('SEARCH_RADIUS_KM', 250)
        radius_deg = radius_km / 111.0
        
        start_time_dt = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "maxradius": f"{radius_deg:.2f}",
            "minmagnitude": self._config.get('MIN_API_MAGNITUDE'),
            "orderby": "time",
            "starttime": start_time_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
        }
        
        return self.API_URL, params, headers

    def _parse_response(self, response_text: str) -> list[EarthquakeEvent]:
        events = []
        try:
            if not response_text or not response_text.strip().startswith('<'):
                self._log.warning(f"[{self.name}] Received empty or non-XML response. Skipping.")
                return []
            
            root = ET.fromstring(response_text)
            
            ns = {
                'q': "http://quakeml.org/xmlns/quakeml/1.2",
                'bed': "http://quakeml.org/xmlns/bed/1.2"
            }
            
            event_params = root.find('bed:eventParameters', ns)
            if event_params is None:
                return []

            for event in event_params.findall('bed:event', ns):
                event_id = event.get('{http://quakeml.org/xmlns/quakeml/1.2}publicID')
                
                def find_text(path):
                    element = event.find(path, ns)
                    return element.text if element is not None else None

                mag_str = find_text('bed:magnitude/bed:mag/bed:value')
                place = find_text('bed:description/bed:text')
                lat_str = find_text('bed:origin/bed:latitude/bed:value')
                lon_str = find_text('bed:origin/bed:longitude/bed:value')
                time_str = find_text('bed:origin/bed:time/bed:value')

                if not all([event_id, mag_str, lat_str, lon_str, time_str]):
                    self._log.warning(f"[{self.name}] Skipping event due to missing essential fields in XML.")
                    continue
                
                aware_dt_object = datetime.fromisoformat(time_str)
                timestamp_sec = int(aware_dt_object.timestamp())

                events.append(EarthquakeEvent(
                    event_id=event_id,
                    magnitude=float(mag_str),
                    place=place or 'Unknown',
                    longitude=float(lon_str),
                    latitude=float(lat_str),
                    timestamp=timestamp_sec
                ))

            return events
        except (ET.ParseError, ValueError, TypeError) as e:
            self._log.error(f"[{self.name}] Unexpected error during XML parsing: {e}", exc_info=True)
            return []