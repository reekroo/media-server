#!/usr/bin/env python3

import logging
import sys
import os

from logging.handlers import RotatingFileHandler

def setup_logger(logger_name, log_file, level=logging.INFO):
    
    log_dir = os.path.dirname(log_file)
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger