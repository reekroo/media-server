import os
from pathlib import Path

source_dirs_env = os.getenv("BACKUP_SOURCE_DIRS", "/mnt/storage/configs")
SOURCE_DIRECTORIES = [d.strip() for d in source_dirs_env.split(',')]

TEMP_ARCHIVE_PATH = Path(os.getenv("BACKUP_TEMP_PATH", "/tmp/backups"))

SCHEDULE_UNIT = os.getenv("SCHEDULE_UNIT", "weeks")
SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", 1))
SCHEDULE_DAY = os.getenv("SCHEDULE_DAY", "sunday")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "03:00")

GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
CREDENTIALS_FILE_PATH = Path(os.getenv("CREDENTIALS_FILE_PATH", "/config/credentials.json"))
TOKEN_FILE_PATH = Path(os.getenv("TOKEN_FILE_PATH", "/config/token.json"))
SCOPES = ['https://www.googleapis.com/auth/drive.file']

LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", "/app/logs/backup_service.log"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))