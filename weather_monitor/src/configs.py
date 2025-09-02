import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'weather_service.log')
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5

WEATHER_SERVICE_SOCKET = "/tmp/weather_service.sock"
LOCATION_SERVICE_SOCKET = '/tmp/location_service.sock'

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "bfff0720b491083abffe6d560e8c5e5f")
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY", "a66c1a552fe64810a8653549252308")

DEFAULT_LATITUDE = 38.4237
DEFAULT_LONGITUDE = 27.1428

INTERVAL_SECONDS = 1800

OUTPUT_MODES = ['console', 'socket']