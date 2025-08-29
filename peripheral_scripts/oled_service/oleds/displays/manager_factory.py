#!/usr/bin/env python3
from __future__ import annotations
import os
from oleds.displays.manager_base import BaseDisplayManager
from oleds.displays.statusbars.statusbar_x8 import StatusBarMono8
from oleds.displays.statusbars.statusbar_x16 import StatusBarGray16
from oleds.displays.ui.statusbar import StatusBar16
from oleds.displays.capabilities import Capabilities
from oleds.configs.oled_profiles import PROFILES, OledProfile
from oleds.configs.themes import get_theme

class MonoDisplayManager(BaseDisplayManager):
    def __init__(self, driver, profile: OledProfile):
        theme = get_theme("ssd1306")
        super().__init__(driver, profile, theme)
        self.statusbar = StatusBarMono8(theme.statusbar_icon, profile.image_mode)
        self.capabilities = Capabilities(
            supports_gray=False,
            supports_animation=True,
            supports_charts=True,
            target_fps=15,
        )

class GrayDisplayManager(BaseDisplayManager):
    def __init__(self, driver, profile: OledProfile):
        theme = get_theme("ssd1327")
        super().__init__(driver, profile, theme)
        self.statusbar = StatusBar16()
        self.capabilities = Capabilities(
            supports_gray=True,
            supports_animation=True,
            supports_charts=True,
            target_fps=20,
        )

def _detect_profile_name(driver, forced: str | None) -> str:
    if forced:
        return forced
    
    name = driver.__class__.__name__.lower()
    
    if "1327" in name:
        return "ssd1327"
    
    if "1306" in name:
        return "ssd1306"
    
    return "ssd1327" if getattr(driver, "height", 64) >= 96 else "ssd1306"

def make_display_manager(driver, profile_name: str | None = None):
    forced = profile_name or os.getenv("OLED_PROFILE")
    prof_key = _detect_profile_name(driver, forced)
    profile = PROFILES[prof_key]

    if prof_key == "ssd1306":
        return MonoDisplayManager(driver, profile)

    return GrayDisplayManager(driver, profile)
