#!/usr/bin/env python3
from typing import Dict
from PIL import Image, ImageDraw, ImageFont
from configs.oled_icons import ICON_DATA
from configs.oled_profiles import OledProfile

WHITE_1BIT = 255
WHITE_RGB = (255, 255, 255)

class BaseDisplayManager:
    """
    Базовый менеджер: отвечает за холст, шрифты, иконки и общий цикл.
    Конкретные потомки определяют image_mode, размеры, статус-бар стратегию.
    """
    def __init__(self, driver, profile: OledProfile):
        self.driver = driver
        self.profile = profile
        self.width = driver.width
        self.height = driver.height

        # холст
        self.image = Image.new(self.profile.image_mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # шрифты
        self.font_small = self._load_font(self.profile.font_path, self.profile.font_small)
        self.font = self._load_font(self.profile.font_path, self.profile.font_regular)
        self.font_large = self._load_font(self.profile.font_path, self.profile.font_large)

        # иконки
        self.icons = {}
        self._prepare_icons()

        self._last_stats: Dict = {}
        self.statusbar = None  # установить в наследнике

    # ---------- abstract-ish hooks ----------
    def _background_color(self):
        return (0, 0, 0) if self.profile.image_mode != "1" else 0

    def color(self):
        return WHITE_RGB if self.profile.image_mode != "1" else WHITE_1BIT

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

    # ---------- utils ----------
    def _load_font(self, path: str, size: int):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def _prepare_icons(self):
        # базовые 8×8 1-бит → масштаб до profile.statusbar_icon и конверт в image_mode
        size = (self.profile.statusbar_icon, self.profile.statusbar_icon)
        upscale = self.profile.statusbar_icon != 8
        for name, data in ICON_DATA.items():
            icon = Image.frombytes('1', (8, 8), bytes(data))
            if upscale:
                icon = icon.resize(size, Image.NEAREST)
            if self.profile.image_mode != '1':
                icon = icon.convert(self.profile.image_mode)
            self.icons[name] = icon

    def _get_icon(self, name: str):
        return self.icons.get(name)
