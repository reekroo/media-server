# weather-monitor

`weather-monitor` is a Python daemon that periodically fetches current weather data from external APIs and makes it available for other local services (e.g., OLED dashboards).
It supports multiple weather providers, flexible location sources, and dual outputs (console + socket).

# Key features

- Provider fallback

    -  OpenWeatherMapProvider (OpenWeatherMap API)

    -  WeatherApiProvider (WeatherAPI.com)
    The first successful provider result is used.

- Location sources

    - SocketLocationProvider: reads coordinates from your running location-service via a UNIX socket. 

    - ConfigLocationProvider: falls back to static lat/lon if the socket is unavailable. 

- Outputs

    - ConsoleOutput: logs weather data in a readable form.

    - SocketOutput: serves the latest weather snapshot as JSON over a UNIX socket (e.g., /tmp/weather_service.sock).

- Unified data model
Weather data is normalized into a single WeatherData namedtuple:

```bash
location_name, temperature, feels_like, pressure, humidity,
description, wind_speed, source
``` :contentReference[oaicite:2]{index=2}
```

- Rotating logging
Console + file logger with rotation (ConcurrentRotatingFileHandler).

- CLI entrypoint
Installed as weather-monitor via pyproject.toml.

# Project Structure

```bash
weather-monitor/
├─ configs.py             # env/config: API keys, intervals, sockets
├─ main.py                # entrypoint wiring (providers, outputs, loop)
├─ weather_controller.py  # core loop: get location → query providers → publish
├─ weather_logger.py      # rotating file logger setup
├─ weather_data.py        # WeatherData namedtuple (normalized model)
├─ providers/
│  ├─ openweathermap.py   # OpenWeatherMap provider
│  ├─ weatherapi.py       # WeatherAPI provider
│  ├─ socket_provider.py  # location via UNIX socket
│  └─ config_provider.py  # fallback lat/lon provider
├─ outputs/
│  ├─ console_output.py   # console summary
│  └─ socket_output.py    # JSON socket server
└─ utils/
   └─ http_client.py      # tiny requests wrapper
```

# Configuration

| Variable                                 | Default                      | Purpose                         |
| ---------------------------------------- | ---------------------------- | ------------------------------- |
| `OPENWEATHERMAP_API_KEY`                 | *(none)*                     | API key for OpenWeatherMap      |
| `WEATHERAPI_API_KEY`                     | *(none)*                     | API key for WeatherAPI          |
| `LOCATION_SERVICE_SOCKET`                | `/tmp/location_service.sock` | Path to location-service socket |
| `WEATHER_SERVICE_SOCKET`                 | `/tmp/weather_service.sock`  | Where to serve weather JSON     |
| `DEFAULT_LATITUDE` / `DEFAULT_LONGITUDE` | `38.4237 / 27.1428`          | Fallback location               |
| `INTERVAL_SECONDS`                       | `1800`                       | Refresh interval (seconds)      |
| `LOG_FILE_PATH`                          | `logs/weather_service.log`   | Rotating file log path          |

# Installation

Requires Python ≥ 3.9. Declared dependencies: requests, concurrent-log-handler.

Install inside your virtual environment or system

```bash
pip install .
```

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-monitor
sudo systemctl start weather-monitor
```

# Typical JSON payload

```json
{
  "location_name": "Izmir",
  "temperature": 26.1,
  "feels_like": 27.8,
  "pressure": 1015,
  "humidity": 65,
  "description": "Clear sky",
  "wind_speed": 12,
  "source": "OpenWeatherMap"
}
```