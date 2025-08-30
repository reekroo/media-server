from .configs import UPS_LOG_FILE
from .ups_manager import UpsManager
from utils.logger import setup_logger 

def main():
    log = setup_logger("UpsService", UPS_LOG_FILE)

    mgr = UpsManager(logger=log)
    try:
        mgr.loop()
    except KeyboardInterrupt:
        log.info("Interrupted by user")

if __name__ == "__main__":
    main()