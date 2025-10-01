import os

PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/app")
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

WEATHER_SERVICE_SOCKET = os.getenv("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")
ON_DEMAND_WEATHER_SOCKET = os.getenv("ON_DEMAND_WEATHER_SOCKET", "/tmp/on_demand_weather.sock")
LOCATION_SERVICE_SOCKET = os.getenv('LOCATION_SERVICE_SOCKET', '/tmp/location_service.sock')
WEATHER_JSON_FILE_PATH = os.getenv("WEATHER_JSON_FILE_PATH", "/run/monitors/weather/latest.json")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", os.path.join(LOGS_DIR, 'weather_service.log'))

LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 1800))
JSON_INTERVAL_SECONDS = int(os.getenv("JSON_INTERVAL_SECONDS", 1200))

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY")

DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", 38.4237))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", 27.1428))

OUTPUT_MODES = ['console', 'socket']