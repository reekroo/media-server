import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SOCKET_FILE = "/tmp/weather_service.sock"
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, 'app.log')

LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "bfff0720b491083abffe6d560e8c5e5f")
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY", "a66c1a552fe64810a8653549252308")

LATITUDE = 38.4237
LONGITUDE = 27.1428

INTERVAL_SECONDS = 1800

OUTPUT_MODES = ['console', 'socket']