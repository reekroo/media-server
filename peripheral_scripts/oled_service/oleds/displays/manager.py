#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict
from .manager_factory import make_display_manager

class DisplayManager:
    """
    Тонкая обёртка над конкретной реализацией менеджера дисплея.
    Все неизвестные атрибуты/методы делегируются во внутренний объект.
    """
    def __init__(self, driver, profile_name: str | None = None):
        self._impl = make_display_manager(driver, profile_name)
        self.driver = driver  # оставим, чтобы код мог обращаться напрямую

    # универсальная прокся: всё, чего нет в обёртке, берём из _impl
    def __getattr__(self, name: str):
        return getattr(self._impl, name)

    # Явные пробросы основных действий (не обязательно, но читаемо)
    def begin(self, stats: Dict): return self._impl.begin(stats)
    def clear(self): return self._impl.clear()
    def show(self): return self._impl.show()
    def draw_status_bar(self, statuses: Dict): return self._impl.draw_status_bar(statuses)
    def color(self): return self._impl.color()
