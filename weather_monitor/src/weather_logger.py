import logging
import sys
import os

from configs import LOG_MAX_BYTES, LOG_BACKUP_COUNT
from concurrent_log_handler import ConcurrentRotatingFileHandler

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