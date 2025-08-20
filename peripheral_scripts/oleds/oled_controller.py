#!/usr/bin/env python3

import time
import sys

sys.path.append('/home/reekroo/scripts')

from oleds.providers.stats_provider import StatsProvider
from oleds.displays.display_manager import DisplayManager
from common.logger import setup_logger

log = setup_logger('OledController', '/home/reekroo/scripts/logs/oled.log')

class OledController:

    def __init__(self):
        self.provider = StatsProvider()
        self.display = DisplayManager()
        log.info("[OledController] Initialized.")

    def run(self, page_interval=10, update_interval=2):
        log.info("[OledController] Entering main loop.")
        current_page = 0
        last_page_switch = time.time()
        
        while True:
            try:
                if time.time() - last_page_switch > page_interval:
                    current_page = (current_page + 1) % 3
                    last_page_switch = time.time()
                    log.debug(f"[OledController] Switching to page {current_page + 1}")

                stats = self.provider.get_all_stats()

                self.display.clear()
                
                self.display.draw_status_bar(stats)

                if current_page == 0:
                    self.display.draw_page_performance(stats)
                elif current_page == 1:
                    self.display.draw_page_storage(stats)
                elif current_page == 2:
                    self.display.draw_page_health(stats)

                self.display.show()
                time.sleep(update_interval)
                
            except Exception as e:
                log.error(f"[OledController] An error occurred in the main loop: {e}", exc_info=True)
                time.sleep(10)

if __name__ == '__main__':
    try:
        controller = OledController()
        controller.run()
    except KeyboardInterrupt:
        log.info("[OledController] stopped by user.")
    except Exception as e:
        log.critical(f"[OledController] failed to start: {e}", exc_info=True)