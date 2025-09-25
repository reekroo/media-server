import logging
import sys
import os

from concurrent_log_handler import ConcurrentRotatingFileHandler

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'ai_hub.log')
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5

def setup_logger(logger_name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger

    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(console_formatter)
    logger.addHandler(stream_handler)

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = ConcurrentRotatingFileHandler(
            filename=log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("File logging disabled: %s", e)

    return logger