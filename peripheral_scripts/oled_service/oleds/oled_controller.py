#!/usr/bin/env python3

import time
from .providers.stats_provider import StatsProvider
from utils.logger import setup_logger

log = setup_logger('OledController', '/home/reekroo/peripheral_scripts/logs/oled.log')

class OledController:
    def __init__(self, display_manager, pages):
        self.provider = StatsProvider()
        self.display = display_manager
        self.pages = pages
        self.current_page_index = 0
        
        log.info(f"[OledController] Initialized with {len(self.pages)} pages.")

    def run(self, page_interval=10, update_interval=2):
        log.info("[OledController] Entering main loop.")
        last_page_switch = time.time()
        
        if not self.pages:
            log.warning("[OledController] No pages to display. Exiting loop.")
            return

        while True:
            try:
                if time.time() - last_page_switch > page_interval:
                    self.current_page_index = (self.current_page_index + 1) % len(self.pages)
                    last_page_switch = time.time()
                    log.debug(f"[OledController] Switching to page {self.current_page_index + 1}")

                stats = self.provider.get_all_stats()
                
                self.display.clear()
                self.display.draw_status_bar(stats)

                active_page = self.pages[self.current_page_index]
                active_page.draw(self.display, stats)

                self.display.show()
                time.sleep(update_interval)
                
            except Exception as e:
                log.error(f"[OledController] An error occurred in the main loop: {e}", exc_info=True)
                time.sleep(10)