#!/usr/bin/env python3
import time
from configs.configs import LOG_FILE, PAGE_INTERVAL, UPDATE_INTERVAL
from providers.stats_provider import StatsProvider
from utils.logger import setup_logger

log = setup_logger('OledController', LOG_FILE)

class OledController:
    """
    Главный цикл отрисовки:
      - собираем stats
      - выбираем активную страницу
      - если страница определила should_render(...) и он False — пропускаем её
      - рендерим: либо контроллер рисует фон/статус-бар, либо это делает страница (HANDLES_BACKGROUND = True)
      - меняем страницу по таймеру page_interval
    """
    def __init__(self, display_manager, pages):
        self.provider = StatsProvider()
        self.display = display_manager
        self.pages = list(pages) if pages else []
        self.current_page_index = 0
        log.info("[OledController] Initialized with %d pages.", len(self.pages))

    def _next_index(self, idx: int) -> int:
        return (idx + 1) % len(self.pages)

    def _pick_renderable_page(self, stats) -> bool:
        """
        Выбирает первую подходящую страницу, начиная с current_page_index.
        Возвращает True, если нашли страницу для рендера (current_page_index обновлён при необходимости).
        Возвращает False, если ни одна страница не подходит (все should_render=False).
        """
        if not self.pages:
            return False

        attempts = 0
        idx = self.current_page_index
        while attempts < len(self.pages):
            page = self.pages[idx]
            can_render = True
            # мягкий контракт: метод необязателен
            if hasattr(page, "should_render"):
                try:
                    can_render = bool(page.should_render(self.display, stats))
                except Exception as e:
                    # если страница упала в should_render — считаем, что она временно недоступна
                    log.debug("[OledController] should_render() failed for %s: %s", page.__class__.__name__, e)
                    can_render = False

            if can_render:
                if idx != self.current_page_index:
                    log.debug("[OledController] Skipping to %s", page.__class__.__name__)
                self.current_page_index = idx
                return True

            idx = self._next_index(idx)
            attempts += 1

        return False

    def run(self, page_interval: int | None = None, update_interval: int | None = None):
        page_interval = page_interval or PAGE_INTERVAL
        update_interval = update_interval or UPDATE_INTERVAL

        log.info("[OledController] Entering main loop. page_interval=%ss, update_interval=%ss",
                 page_interval, update_interval)

        if not self.pages:
            log.warning("[OledController] No pages to display.")
            return

        # таймер переключения страниц
        next_switch_ts = time.monotonic() + page_interval

        while True:
            try:
                stats = self.provider.get_all_stats()

                # 1) выбрать страницу (с учётом should_render)
                found = self._pick_renderable_page(stats)
                if not found:
                    # никого подходящего — засыпаем маленькими шагами
                    time.sleep(update_interval)
                    continue

                active_page = self.pages[self.current_page_index]

                # 2) переключение страницы по таймеру
                now = time.monotonic()
                if now >= next_switch_ts:
                    # переключаемся и даём новой странице полноценный слот времени
                    self.current_page_index = self._next_index(self.current_page_index)
                    next_switch_ts = now + page_interval
                    # заново выбрать страницу (вдруг новая не рендерится)
                    found = self._pick_renderable_page(stats)
                    if not found:
                        time.sleep(update_interval)
                        continue
                    active_page = self.pages[self.current_page_index]

                # 3) фон/статус-бар — либо контроллер, либо страница
                handles_bg = bool(getattr(active_page, "HANDLES_BACKGROUND", False))
                if not handles_bg:
                    self.display.clear()
                    self.display.draw_status_bar(stats)

                # 4) собственно отрисовка страницы
                active_page.draw(self.display, stats)

                # 5) если страница сама не вызвала show(), всё равно финализируем кадр
                try:
                    self.display.show()
                except Exception:
                    # без фанатизма — некоторые страницы уже показали кадр сами
                    pass

                time.sleep(update_interval)

            except Exception as e:
                log.error("[OledController] Error in main loop: %s", e, exc_info=True)
                time.sleep(10)
