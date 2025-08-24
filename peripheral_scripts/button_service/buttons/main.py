from .button_controller import ButtonController
from utils.logger import setup_logger
from .configs.configs import BUTTONS_LOG_FILE

log = setup_logger('ButtonMain', BUTTONS_LOG_FILE)

def main():
    controller = ButtonController()
    try:
        controller.run()
    except KeyboardInterrupt:
        log.info("Button service stopped by user.")
    finally:
        controller.close()

if __name__ == '__main__':
    main()
