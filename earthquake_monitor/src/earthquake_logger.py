import sys
sys.path.append('/home/reekroo/scripts')
from common.logger import setup_logger
from src.configs import LOG_FILE_PATH

def get_logger(name):
    return setup_logger(name, LOG_FILE_PATH)