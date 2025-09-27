import asyncio
import json
import logging
from typing import Optional, Any, Dict
from core.settings import Settings

log = logging.getLogger(__name__)

class EarthquakeSocketClient:
    def __init__(self, settings: Settings):
        self._socket_path = settings.ON_DEMAND_EARTHQUAKE_SOCKET
        self._buffer_size = 8192

    async def get_earthquakes(self, lat: float, lon: float, days: int = 1) -> Optional[Dict[str, Any]]:
        log.info(f"Requesting earthquake data for ({lat},{lon}) for last {days} day(s)...")
        try:
            reader, writer = await asyncio.open_unix_connection(self._socket_path)
        except (ConnectionRefusedError, FileNotFoundError):
            log.error(f"Earthquake service is unavailable at socket: {self._socket_path}")
            return {"error": "Earthquake service is currently unavailable."}

        try:
            request_payload = {"lat": lat, "lon": lon, "days": days}
            writer.write(json.dumps(request_payload).encode('utf-8'))
            await writer.drain()

            raw_response = await reader.read(self._buffer_size)
            response = json.loads(raw_response.decode('utf-8'))
            
            if response.get("status") == "success":
                return response.get("data")
            else:
                return {"error": response.get("message", "Unknown error from earthquake service.")}
        except Exception as e:
            log.error(f"Failed to communicate with the earthquake service: {e}", exc_info=True)
            return {"error": "Failed to communicate with the earthquake service."}
        finally:
            writer.close()
            await writer.wait_closed()