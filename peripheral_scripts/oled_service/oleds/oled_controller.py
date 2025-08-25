#!/usr/bin/env python3
import time
from utils.logger import setup_logger
from configs.configs import LOG_FILE, PAGE_INTERVAL, UPDATE_INTERVAL
from providers.stats_provider import StatsProvider

log = setup_logger('OledController', LOG_FILE)

class OledController:
    def __init__(self, display_manager, pages):
        self.provider = StatsProvider()
        self.display = display_manager
        self.pages = list(pages) if pages else []
        self.current_page_index = 0
        log.info("[OledController] Initialized with %d pages.", len(self.pages))

    def run(self, page_interval: int | None = None, update_interval: int | None = None):
        page_interval = page_interval or PAGE_INTERVAL
        update_interval = update_interval or UPDATE_INTERVAL

        log.info("[OledController] Entering main loop. page_interval=%ss, update_interval=%ss",
                 page_interval, update_interval)

        if not self.pages:
            log.warning("[OledController] No pages to display. Exiting loop.")
            return

        last_page_switch = time.time()

        while True:
            try:
                # page switch
                now = time.time()
                if now - last_page_switch > page_interval:
                    self.current_page_index = (self.current_page_index + 1) % len(self.pages)
                    last_page_switch = now
                    log.debug("[OledController] Switching to page %d", self.current_page_index + 1)

                stats = self.provider.get_all_stats()

                self.display.clear()
                self.display.draw_status_bar(stats)

                active_page = self.pages[self.current_page_index]
                active_page.draw(self.display, stats)

                self.display.show()
                time.sleep(update_interval)

            except Exception as e:
                log.error("[OledController] Error in main loop: %s", e, exc_info=True)
                time.sleep(10)
