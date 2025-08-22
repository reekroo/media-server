import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import configs
from earthquake_logger import get_logger
from data_sources.base import DataSource

log = get_logger(__name__)

class IscApiDataSource(DataSource):
    API_URL = "https://www.isc.ac.uk/fdsnws/event/1/query"

    def _parse_quakeml(self, xml_string):
        try:
            if not xml_string or not xml_string.strip().startswith('<'):
                log.warning("[IscApiDataSource] Received empty or non-XML response. Skipping.")
                return None
            
            root = ET.fromstring(xml_string)
            event_parameters = root.find('{http://quakeml.org/xmlns/bed/1.2}eventParameters')

            if event_parameters is None:
                return None

            features = []
            for event in event_parameters.findall('{http://quakeml.org/xmlns/bed/1.2}event'):
                event_id = event.get('{http://quakeml.org/xmlns/quakeml/1.2}publicID')
                
                desc = event.find('{http://quakeml.org/xmlns/bed/1.2}description/{http://quakeml.org/xmlns/bed/1.2}text')
                mag_value = event.find('{http://quakeml.org/xmlns/bed/1.2}magnitude/{http://quakeml.org/xmlns/bed/1.2}mag/{http://quakeml.org/xmlns/bed/1.2}value')
                
                feature = {
                    'type': 'Feature',
                    'id': event_id,
                    'properties': {
                        'mag': float(mag_value.text) if mag_value is not None else None,
                        'place': desc.text if desc is not None else 'Unknown',
                    }
                }
                features.append(feature)

            return {'features': features}
        except Exception as e:
            log.error(f"[IscApiDataSource] Unexpected error during XML parsing: {e}", exc_info=True)
            return None
        
    def get_earthquakes(self):
        log.info("[IscApiDataSource] Querying ISC data source...")
        
        time_window = timedelta(minutes=configs.API_TIME_WINDOW_MINUTES)
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc - time_window
        radius_deg = configs.SEARCH_RADIUS_KM / 111.0

        params = {
            "latitude": configs.MY_LAT,
            "longitude": configs.MY_LON,
            "maxradius": f"{radius_deg:.2f}",
            "minmagnitude": configs.MIN_API_MAGNITUDE,
            "orderby": "time",
            "starttime": start_time_utc.strftime('%Y-%m-%dT%H:%M:%S'),
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(self.API_URL, params=params, headers=headers, timeout=10)
                        
            if response.status_code == 204:
                log.info("[IscApiDataSource] Received 204 No Content, no new events.")
                return None 
            
            log.info(f"[IscApiDataSource] Response status code: {response.status_code}")
            response.raise_for_status()
            
            return self._parse_quakeml(response.text)
        
        except requests.RequestException as e:
            log.error(f"[IscApiDataSource] Network or API error: {e}")
            return None