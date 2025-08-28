#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict
from PIL import Image, ImageDraw
from oleds.configs.oled_profiles import OledProfile
from oleds.configs.themes import Theme, IconProvider

WHITE_1BIT = 255
WHITE_RGB = (255, 255, 255)

class BaseDisplayManager:
    """
    Базовый менеджер: холст, шрифты (из Theme), иконки (IconProvider),
    общий цикл begin/clear/show, цветовая схема.
    Потомки подключают статус-бар стратегию.
    """
    def __init__(self, driver, profile: OledProfile, theme: Theme):
        self.driver = driver
        self.profile = profile
        self.theme = theme

        self.width = driver.width
        self.height = driver.height

        # холст
        self.image = Image.new(self.profile.image_mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # шрифты из темы
        self.font_small = self.theme.load_font(self.theme.font_small)
        self.font = self.theme.load_font(self.theme.font_regular)
        self.font_large = self.theme.load_font(self.theme.font_large)

        # иконки из темы (или 8x8 upscale)
        self._icon_provider = IconProvider(self.profile.image_mode, self.theme.statusbar_icon, self.theme.icon_pack)
        self.icons = {}  # cache

        self._last_stats: Dict = {}
        self.statusbar = None  # установить в наследнике

    # ---------- colors ----------
    def _background_color(self):
        return self.theme.background

    def color(self):
        return self.theme.foreground

    # ---------- public ----------
    def begin(self, stats: Dict):
        self._last_stats = stats
        self.clear()

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), fill=self._background_color())

    def show(self):
        self.driver.show(self.image)

    def draw_status_bar(self, statuses: Dict):
        if self.statusbar:
            self.statusbar.draw(self, statuses)

    # ---------- icons ----------
    def _get_icon(self, name: str):
        ic = self.icons.get(name)
        if ic is None:
            ic = self._icon_provider.get(name)
            if ic:
                self.icons[name] = ic
        return ic
