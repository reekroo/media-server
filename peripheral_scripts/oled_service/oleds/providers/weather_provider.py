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

class WeatherProvider:
    """
    Клиент для локального UNIX-сокета погодного сервиса.
    Ожидает одну JSON-строку с полями WeatherData (см. модель выше).
    Возвращает WeatherData или None, если данных нет/источник недоступен.
    """

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.getenv("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")

    def get_weather(self, timeout: float = 0.25) -> Optional[WeatherData]:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect(self.path)
            # читаем одну порцию (ожидаем JSON-объект одной строкой)
            raw = s.recv(4096)
            s.close()
            if not raw:
                return None
            txt = raw.decode("utf-8", errors="ignore").strip()
            if not txt:
                return None
            obj = json.loads(txt)
            # допускаем разные кейсы ключей
            def get(k, default=None):
                return obj.get(k, obj.get(k.lower(), default))

            wd = WeatherData(
                location_name = get("location_name", "Unknown"),
                temperature   = float(get("temperature", 0.0)),
                feels_like    = float(get("feels_like", 0.0)),
                pressure      = int(get("pressure", 0)),
                humidity      = int(get("humidity", 0)),
                description   = str(get("description", "")).strip(),
                source        = str(get("source", "n/a")).strip(),
            )
            return wd
        except (FileNotFoundError, ConnectionRefusedError, socket.timeout, json.JSONDecodeError, OSError):
            return None
