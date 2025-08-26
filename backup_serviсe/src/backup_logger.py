import logging
import sys
import os
from . import configs
from concurrent_log_handler import ConcurrentRotatingFileHandler

file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(message)s')

root_logger = logging.getLogger()
root_logger.setLevel(configs.LOG_LEVEL)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

os.makedirs(os.path.dirname(configs.LOG_FILE_PATH), exist_ok=True)

file_handler = ConcurrentRotatingFileHandler(
    filename=configs.LOG_FILE_PATH,
    maxBytes=configs.LOG_MAX_BYTES,
    backupCount=configs.LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(console_formatter)
root_logger.addHandler(stream_handler)

def get_logger(name):
    return logging.getLogger(name)
