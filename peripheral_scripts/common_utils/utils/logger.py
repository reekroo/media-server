from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

try:
    from concurrent_log_handler import ConcurrentRotatingFileHandler as _FileHandler
except Exception:
    _FileHandler = RotatingFileHandler

def setup_logger(logger_name: str,
                log_file: str | None,
                level: int = logging.INFO,
                max_bytes: int = 1 * 1024 * 1024,
                backups: int = 3) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(console_formatter)
    logger.addHandler(stream_handler)

    if log_file:
        try:
            log_dir = os.path.dirname(log_file) or "."
            os.makedirs(log_dir, exist_ok=True)

            file_handler = _FileHandler(
                filename=log_file, 
                maxBytes=max_bytes, 
                backupCount=backups, 
                encoding="utf-8"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            logger.warning("File logging disabled: %s", e)

    return logger