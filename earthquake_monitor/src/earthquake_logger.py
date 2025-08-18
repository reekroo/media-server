import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from src.configs import LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT

handler = ConcurrentRotatingFileHandler(
    filename=LOG_FILE_PATH,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

root_logger.addHandler(handler)

def get_logger(name):
    return logging.getLogger(name)