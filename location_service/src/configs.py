import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(LOGS_DIR, 'location.log'))
LOCATION_SERVICE_SOCKET = os.getenv('LOCATION_SERVICE_SOCKET', '/tmp/location_service.sock')
ON_DEMAND_GEOCODING_SOCKET = os.getenv('ON_DEMAND_GEOCODING_SOCKET', '/tmp/geocoding_service.sock')

LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO")

DEFAULT_LATITUDE = float(os.getenv('DEFAULT_LATITUDE', 38.4237))
DEFAULT_LONGITUDE = float(os.getenv('DEFAULT_LONGITUDE', 27.1428))

UPDATE_INTERVAL_SECONDS = int(os.getenv('UPDATE_INTERVAL_SECONDS', 3600))