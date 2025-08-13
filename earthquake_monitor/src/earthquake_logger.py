# src/earthquake_logger.py

from scripts.common.logger import setup_logger
from src.config import LOG_FILE_PATH

def get_logger(name):
    return setup_logger(name, LOG_FILE_PATH)