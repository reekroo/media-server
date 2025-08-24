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

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if log_file:
        try:
            log_dir = os.path.dirname(log_file) or "."
            os.makedirs(log_dir, exist_ok=True)
            fh = _FileHandler(log_file, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        except Exception as e:
            logger.warning("File logging disabled: %s", e)

    return logger