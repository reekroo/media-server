import sys
sys.path.append('/home/reekroo/scripts')
from common.logger import setup_logger
from src.configs import LOG_FILE_PATH

_service_logger_instance = None

def get_logger(name):
    global _service_logger_instance

    if _service_logger_instance is None:
        print("--- Initializing logger for the first time ---")
        _service_logger_instance = setup_logger('earthquake_service', LOG_FILE_PATH)

    return setup_logger(name, LOG_FILE_PATH)