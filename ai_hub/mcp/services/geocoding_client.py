import asyncio
import json
import logging
from typing import Optional, Tuple
from core.settings import Settings

log = logging.getLogger(__name__)

class GeocodingSocketClient:
    def __init__(self, settings: Settings):
        self._socket_path = settings.ON_DEMAND_GEOCODING_SOCKET
        self._buffer_size = 2048

    async def get_coords_for_city(self, city_name: str) -> Optional[Tuple[float, float]]:
        log.info(f"Requesting geocoding for city: '{city_name}' via socket...")
        try:
            reader, writer = await asyncio.open_unix_connection(self._socket_path)
        except (ConnectionRefusedError, FileNotFoundError):
            log.error(f"Geocoding service is unavailable at socket: {self._socket_path}")
            return None

        try:
            request_payload = {"city_name": city_name}
            writer.write(json.dumps(request_payload).encode('utf-8'))
            await writer.drain()

            raw_response = await reader.read(self._buffer_size)
            response = json.loads(raw_response.decode('utf-8'))
            
            if response.get("status") == "success":
                lat, lon = response.get("lat"), response.get("lon")
                if lat is not None and lon is not None:
                    log.info(f"Successfully geocoded '{city_name}': ({lat}, {lon})")
                    return float(lat), float(lon)

            log.warning(f"Geocoding service returned an error for '{city_name}': {response.get('message')}")
            return None
        except Exception as e:
            log.error(f"Failed to communicate with the geocoding service: {e}", exc_info=True)
            return None
        finally:
            writer.close()
            await writer.wait_closed()