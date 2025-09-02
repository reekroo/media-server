#!/usr/bin/env python3
import os, socket, json
from collections import namedtuple
from typing import Optional

WeatherData = namedtuple(
    "WeatherData",
    [
        "location_name", 
        "temperature", 
        "feels_like", 
        "pressure",
        "humidity", 
        "description", 
        "source",
    ]
)

def _safe_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _safe_int(value, default=0):
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

class WeatherProvider:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.getenv("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")

    def get_weather(self, timeout: float = 0.25) -> Optional[WeatherData]:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect(self.path)
                raw = s.recv(4096)
                if not raw:
                    return None
            
            txt = raw.decode("utf-8", errors="ignore").strip()
            if not txt:
                return None
            
            obj = json.loads(txt)
            
            wd = WeatherData(
                location_name = str(obj.get("location_name") or "Unknown"),
                temperature   = _safe_float(obj.get("temperature")),
                feels_like    = _safe_float(obj.get("feels_like")),
                pressure      = _safe_int(obj.get("pressure")),
                humidity      = _safe_int(obj.get("humidity")),
                description   = str(obj.get("description") or "").strip(),
                source        = str(obj.get("source") or "n/a").strip(),
            )
            return wd
        
        except Exception:
            return None