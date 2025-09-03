import os
from pathlib import Path

SOURCE_DIRECTORIES = [
    os.getenv("BACKUP_SOURCE_DIR", "/mnt/storage/configs")
]

TEMP_ARCHIVE_PATH = os.getenv("BACKUP_TEMP_PATH", "/tmp/backups")

SCHEDULE_UNIT = "weeks"
SCHEDULE_INTERVAL = 1
SCHEDULE_DAY = "sunday"
SCHEDULE_TIME = "03:00"

GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1m7GaTewj45VfWbikPt09zILbUIVuun46")
CREDENTIALS_FILE_PATH = Path(__file__).parent.parent / "credentials.json"
TOKEN_FILE_PATH = Path(__file__).parent.parent / "token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

LOG_FILE_PATH = Path(__file__).parent.parent / "logs/backup_service.log"
LOG_LEVEL = "INFO"
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3

def setup_directories():
    Path(TEMP_ARCHIVE_PATH).mkdir(parents=True, exist_ok=True)

setup_directories()
