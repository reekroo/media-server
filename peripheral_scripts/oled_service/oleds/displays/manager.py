#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict
from oleds.displays.manager_factory import make_display_manager

class DisplayManager:
    """
    Делегат к выбранному менеджеру (моно/серый).
    Интерфейс сохраняется: image, draw, fonts, begin(), clear(), show(), draw_status_bar(), color(), width/height.
    """
    def __init__(self, driver, profile_name: str | None = None):
        self._impl = make_display_manager(driver, profile_name)
        # прокидываем часто используемые атрибуты:
        self.driver = driver
        self.width = self._impl.width
        self.height = self._impl.height
        self.image = self._impl.image
        self.draw = self._impl.draw
        self.font_small = self._impl.font_small
        self.font = self._impl.font
        self.font_large = self._impl.font_large
        # доступ к теме/способностям при желании в экранах:
        self.theme = getattr(self._impl, "theme", None)
        self.capabilities = getattr(self._impl, "capabilities", None)

    # пробросы
    def begin(self, stats: Dict): self._impl.begin(stats)
    def clear(self): self._impl.clear()
    def show(self): self._impl.show()
    def draw_status_bar(self, statuses: Dict): self._impl.draw_status_bar(statuses)
    def color(self): return self._impl.color()
    def _get_icon(self, name: str): return self._impl._get_icon(name)
    @property
    def _last_stats(self): return getattr(self._impl, "_last_stats", {})
