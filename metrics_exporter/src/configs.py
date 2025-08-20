import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTER_PORT = 8001
EXPORTER_UPDATE_INTERVAL_SECONDS = 15

LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'metrics_exporter.log')
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3