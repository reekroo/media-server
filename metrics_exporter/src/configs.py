import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / 'logs'

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', LOGS_DIR / 'metrics_exporter.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO")

EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', 8001))
EXPORTER_UPDATE_INTERVAL_SECONDS = int(os.getenv('EXPORTER_UPDATE_INTERVAL_SECONDS', 15))

ROOT_DISK_PATH = os.getenv('ROOT_DISK_PATH', '/')
STORAGE_DISK_PATH = os.getenv('STORAGE_DISK_PATH', '/mnt/storage')

LAN_INTERFACE = os.getenv('LAN_INTERFACE', 'eth0')
WLAN_INTERFACE = os.getenv('WLAN_INTERFACE', 'wlan0')