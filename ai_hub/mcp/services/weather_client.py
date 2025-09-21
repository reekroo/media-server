import asyncio
import json
from datetime import date
from typing import Optional, Any, Dict
from core.settings import Settings

class WeatherSocketClient:
    def __init__(self, settings: Settings):
        self._socket_path = settings.ON_DEMAND_WEATHER_SOCKET
        self._buffer_size = 4096

    async def get_weather(self, lat: float, lon: float, requested_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        try:
            reader, writer = await asyncio.open_unix_connection(self._socket_path)
        except (ConnectionRefusedError, FileNotFoundError):
            return {"error": "Weather service is currently unavailable."}

        try:
            request_payload = {
                "lat": lat,
                "lon": lon,
                "date": requested_date.strftime('%Y-%m-%d') if requested_date else None
            }
            writer.write(json.dumps(request_payload).encode('utf-8'))
            await writer.drain()

            raw_response = await reader.read(self._buffer_size)
            response = json.loads(raw_response.decode('utf-8'))
            
            if response.get("status") == "success":
                return response.get("data")
            else:
                return {"error": response.get("message", "Unknown error from weather service.")}
        except Exception:
            return {"error": "Failed to communicate with the weather service."}
        finally:
            writer.close()
            await writer.wait_closed()