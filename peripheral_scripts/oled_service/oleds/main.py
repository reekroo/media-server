#!/usr/bin/env python3
import os

from oled_controller import OledController
from displays.manager import DisplayManager
from displays.screens.performance_screen import PerformanceScreen
from displays.screens.storage_screen import StorageScreen
from displays.screens.health_screen import HealthScreen

from utils.logger import setup_logger
from configs.configs import LOG_FILE

log = setup_logger('OledMain', LOG_FILE)

def _make_driver():
    drv = os.getenv("OLED_DRIVER", "ssd1306").strip().lower()
    if drv == "ssd1327":
        from displays.drivers.ssd1327 import SSD1327_Driver
        return SSD1327_Driver()
    else:
        from displays.drivers.ssd1306 import SSD1306_Driver
        return SSD1306_Driver()

def main():
    try:
        active_driver = _make_driver()

        active_pages = [
            PerformanceScreen(),
            StorageScreen(),
            HealthScreen(),
        ]

        display_manager = DisplayManager(driver=active_driver)

        controller = OledController(
            display_manager=display_manager,
            pages=active_pages
        )

        controller.run()

    except KeyboardInterrupt:
        log.info("[OledController] stopped by user.")
    
    except Exception as e:
        log.critical(f"[OledController] failed to start: {e}", exc_info=True)

if __name__ == '__main__':
    main()
