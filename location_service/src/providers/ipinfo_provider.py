import requests
from .base import ILocationProvider
from location_logger import get_logger

log = get_logger(__name__)

class IpInfoProvider(ILocationProvider):
    def determine_location(self) -> dict | None:
        try:
            log.info("Attempting to determine location via ipinfo.io...")
            
            response = requests.get('https://ipinfo.io/json', timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            lat, lon = map(float, data['loc'].split(','))
            log.info("Successfully determined location from IP: (%s, %s)", lat, lon)
            
            return {'lat': lat, 'lon': lon}
        
        except Exception as e:
            log.error("Failed to get location from ipinfo.io: %s", e)
            return None