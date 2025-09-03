#!/usr/bin/env python3
import os
import socket
import json
import logging
import time
from collections import namedtuple
from typing import Optional

WeatherData = namedtuple(
    "WeatherData",
    [
        "location_name", "temperature", "feels_like", "pressure",
        "humidity", "description", "source",
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
    def __init__(self, logger: logging.Logger, path: Optional[str] = None):
        self._log = logger
        self.path = path or os.getenv("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")
        self._log.info(f"WeatherProvider initialized for socket path: {self.path}")

    def get_weather(self, timeout: float = 2.0) -> Optional[WeatherData]:
        for attempt in range(3):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    s.connect(self.path)
                    raw = s.recv(4096)
                    if not raw:
                        continue
                
                txt = raw.decode("utf-8", errors="ignore").strip()
                if not txt:
                    continue

                obj = json.loads(txt)
                
                return WeatherData(
                    location_name=str(obj.get("location_name") or "Unknown"),
                    temperature=_safe_float(obj.get("temperature")),
                    feels_like=_safe_float(obj.get("feels_like")),
                    pressure=_safe_int(obj.get("pressure")),
                    humidity=_safe_int(obj.get("humidity")),
                    description=str(obj.get("description") or "").strip(),
                    source=str(obj.get("source") or "n/a").strip(),
                )
            
            except Exception as e:
                self._log.warning(f"Failed to get weather on attempt {attempt+1}: {e}")
                if attempt < 2:
                    time.sleep(1)
        
        self._log.error("Failed to get weather data after all attempts.")
        return None