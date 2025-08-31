#!/usr/bin/env python3
from __future__ import annotations

from oleds.displays.manager_base import BaseDisplayManager
from oleds.displays.capabilities import Capabilities
from oleds.configs.oled_profiles import OledProfile
from oleds.configs.themes import get_theme

from oleds.displays.statusbars.ssd1327 import StatusBarSSD1327, BarConfig

class GrayDisplayManager(BaseDisplayManager):

    def __init__(self, driver, profile: OledProfile):
        theme = get_theme("ssd1327")
        super().__init__(driver, profile, theme)

        self.status_bar_height = 20

        cfg = BarConfig(
            pad_top=2,
            pad_bot=2,
            elem_h=16,
            gap=2,
            right_gap_between=2,
            clock_fmt="%H:%M",
            battery_width=24,
            left_icons=("docker", "wifi", "bluetooth"),
        )

        fg, bg = 255, 0

        self.statusbar = StatusBarSSD1327(fg=fg, bg=bg, config=cfg)

        self.capabilities = Capabilities(
            supports_gray=True,
            supports_animation=True,
            supports_charts=True,
            target_fps=20,
        )