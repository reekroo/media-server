#!/usr/-bin/env python3

from .oled_controller import OledController
from .displays.manager import DisplayManager
from .displays.drivers.ssd1306 import SSD1306_Driver
from .displays.screens.performance_screen import PerformanceScreen
from .displays.screens.storage_screen import StorageScreen
from .displays.screens.health_screen import HealthScreen
from utils.logger import setup_logger

log = setup_logger('OledMain', '/home/reekroo/peripheral_scripts/logs/oled.log')

def main():
    try:
        active_driver = SSD1306_Driver()

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