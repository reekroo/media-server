import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(LOGS_DIR, 'earthquake_monitor.log'))
ON_DEMAND_EARTHQUAKE_SOCKET = os.getenv('ON_DEMAND_EARTHQUAKE_SOCKET', "/tmp/on_demand_earthquake.sock")
LOCATION_SERVICE_SOCKET = os.getenv('LOCATION_SERVICE_SOCKET', '/tmp/location_service.sock')
BUZZER_SOCKET = os.getenv('BUZZER_SOCKET', "/tmp/buzzer.sock")
HISTORICAL_JSON_FILE_PATH = os.getenv('HISTORICAL_JSON_FILE_PATH', '/run/monitors/earthquakes/last7d.json')

LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

DEFAULT_LATITUDE = float(os.getenv('DEFAULT_LATITUDE', 38.4237))
DEFAULT_LONGITUDE = float(os.getenv('DEFAULT_LONGITUDE', 27.1428))
SEARCH_RADIUS_KM = int(os.getenv('SEARCH_RADIUS_KM', 250))

CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
HISTORICAL_INTERVAL_SECONDS = int(os.getenv('HISTORICAL_INTERVAL_SECONDS', 20 * 60))
API_TIME_WINDOW_MINUTES = int(os.getenv('API_TIME_WINDOW_MINUTES', 15))
MAX_PROCESSED_EVENTS_MEMORY = int(os.getenv('MAX_PROCESSED_EVENTS_MEMORY', 10))

ALERT_LEVELS = [
    {'min_magnitude': 7.0, 'duration': 180, 'level_id': 5, 'melody_name': 'ALERT_LEVEL_5'},
    {'min_magnitude': 6.0, 'duration': 60, 'level_id': 4, 'melody_name': 'ALERT_LEVEL_4'},
    {'min_magnitude': 5.0, 'duration': 45, 'level_id': 3, 'melody_name': 'ALERT_LEVEL_3'},
    {'min_magnitude': 4.2, 'duration': 20, 'level_id': 2, 'melody_name': 'ALERT_LEVEL_2'},
    {'min_magnitude': 3.5, 'duration': 10, 'level_id': 1, 'melody_name': 'ALERT_LEVEL_1'},
]

MIN_API_MAGNITUDE = min(level['min_magnitude'] for level in ALERT_LEVELS) if ALERT_LEVELS else 3.0