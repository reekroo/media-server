import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, 'logs/earthquake_monitor.log')

MY_LAT = 38.4237
MY_LON = 27.1428
SEARCH_RADIUS_KM = 250

CHECK_INTERVAL_SECONDS = 60
API_TIME_WINDOW_MINUTES = 15
MAX_PROCESSED_EVENTS_MEMORY = 10

BUZZER_PIN = 18

ALERT_LEVELS = [
    {
        'min_magnitude': 7.0,
        'duration': 180,
        'melody_name': 'ALERT_LEVEL_5'
    },
    {
        'min_magnitude': 6.0,
        'duration': 60,
        'melody_name': 'ALERT_LEVEL_4'
    },
    {
        'min_magnitude': 5.0,
        'duration': 45,
        'melody_name': 'ALERT_LEVEL_3'
    },
    {
        'min_magnitude': 4.2,
        'duration': 20,
        'melody_name': 'ALERT_LEVEL_2'
    },
    {
        'min_magnitude': 3.5,
        'duration': 10,
        'melody_name': 'ALERT_LEVEL_1'
    },
]

MIN_API_MAGNITUDE = min(level['min_magnitude'] for level in ALERT_LEVELS) if ALERT_LEVELS else 3.0
