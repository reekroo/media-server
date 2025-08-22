import os
import logging

from configs import LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT
from concurrent_log_handler import ConcurrentRotatingFileHandler

os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = ConcurrentRotatingFileHandler(
    filename=LOG_FILE_PATH,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

def get_logger(name):
    return logging.getLogger(name)