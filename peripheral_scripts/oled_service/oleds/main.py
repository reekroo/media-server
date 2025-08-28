#!/usr/bin/env python3
import os
from utils.logger import setup_logger
from configs.configs import LOG_FILE

from displays.manager import DisplayManager

log = setup_logger('OledMain', LOG_FILE)

def _make_driver():
    drv = os.getenv("OLED_DRIVER", "ssd1306").strip().lower()
    if drv == "ssd1327":
        from displays.drivers.ssd1327 import SSD1327_Driver
        return SSD1327_Driver()
    else:
        from displays.drivers.ssd1306 import SSD1306_Driver
        return SSD1306_Driver()

def _make_pages(profile_name: str):
    # Старые моно-экраны
    if profile_name == "ssd1306":
        from displays.screens.performance_screen import PerformanceScreen  # 128x64
        from displays.screens.storage_screen import StorageScreen
        from displays.screens.health_screen import HealthScreen
        return [PerformanceScreen(), StorageScreen(), HealthScreen()]
    # Новые серые экраны
    else:
        from displays.screens.performance_screen_1327 import PerformanceScreen1327
        from displays.screens.storage_screen_1327 import StorageScreen1327
        from displays.screens.health_screen_1327 import HealthScreen1327
        return [PerformanceScreen1327(), StorageScreen1327(), HealthScreen1327()]

def main():
    try:
        driver = _make_driver()
        profile = "ssd1327" if "1327" in driver.__class__.__name__.lower() else os.getenv("OLED_DRIVER", "ssd1306")
        pages = _make_pages(profile)

        display_manager = DisplayManager(driver=driver, profile_name=profile)

        from oled_controller import OledController
        controller = OledController(display_manager=display_manager, pages=pages)
        controller.run()

    except KeyboardInterrupt:
        log.info("[OledController] stopped by user.")
    except Exception as e:
        log.critical(f"[OledController] failed to start: {e}", exc_info=True)

if __name__ == '__main__':
    main()
