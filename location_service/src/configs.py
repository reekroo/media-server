import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'location.log')
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5
LOG_LEVEL = "INFO"

DEFAULT_LATITUDE = 38.4237
DEFAULT_LONGITUDE = 27.1428

LOCATION_SERVICE_SOCKET = '/tmp/location_service.sock'

UPDATE_INTERVAL_SECONDS = 3600