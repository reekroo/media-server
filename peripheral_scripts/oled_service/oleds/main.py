#!/usr/bin/env python3
import os

from oleds.configs.configs import LOG_FILE
from oleds.displays.manager import DisplayManager
from oleds.displays.page_factory import make_pages
from utils.logger import setup_logger

log = setup_logger('OledMain', LOG_FILE)

def _make_driver():
    drv = os.getenv("OLED_DRIVER", "ssd1306").strip().lower()
    if drv == "ssd1327":
        from oleds.displays.drivers.ssd1327 import SSD1327_Driver
        return SSD1327_Driver()
    else:
        from oleds.displays.drivers.ssd1306 import SSD1306_Driver
        return SSD1306_Driver()

def main():
    try:
        driver = _make_driver()
        display_manager = DisplayManager(driver=driver)
        pages = make_pages(driver)

        from oleds.oled_controller import OledController
        controller = OledController(display_manager=display_manager, pages=pages)
        controller.run()
    except KeyboardInterrupt:
        log.info("[OledController] stopped by user.")
    except Exception as e:
        log.critical(f"[OledController] failed to start: {e}", exc_info=True)

if __name__ == '__main__':
    main()
