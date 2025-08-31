#!/usr/bin/env python3
from __future__ import annotations

from oleds.displays.manager_base import BaseDisplayManager
from oleds.displays.capabilities import Capabilities
from oleds.configs.oled_profiles import OledProfile
from oleds.configs.themes import get_theme

try:
    from oleds.displays.statusbars.ssd1306 import StatusBarSSD1306
except Exception:
    StatusBarSSD1306 = None

class MonoDisplayManager(BaseDisplayManager):

    def __init__(self, driver, profile: OledProfile):
        theme = get_theme("ssd1306")
        super().__init__(driver, profile, theme)
        
        if StatusBarSSD1306:
            self.statusbar = StatusBarSSD1306(theme.statusbar_icon, profile.image_mode)
        else:
            self.statusbar = None
        
        self.capabilities = Capabilities(
            supports_gray=False,
            supports_animation=False,
            supports_charts=False,
            target_fps=20,
        )
