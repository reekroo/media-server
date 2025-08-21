from buttons.button_controller import ButtonController
from utils.logger import setup_logger

log = setup_logger('ButtonMain', '/home/reekroo/scripts/logs/buttons.log')

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