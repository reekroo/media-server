import logging
import sys
from configs import LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT
from concurrent_log_handler import ConcurrentRotatingFileHandler

file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(message)s')

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

file_handler = ConcurrentRotatingFileHandler(
    LOG_FILE_PATH, 
    maxBytes=LOG_MAX_BYTES, 
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(console_formatter)
root_logger.addHandler(stream_handler)

def get_logger(name):
    return logging.getLogger(name)