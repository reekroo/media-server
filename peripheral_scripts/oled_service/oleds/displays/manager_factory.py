#!/usr/bin/env python3
import os
from .manager_base import BaseDisplayManager
from .statusbars import StatusBarMono8, StatusBarGray16
from configs.oled_profiles import PROFILES, OledProfile

class MonoDisplayManager(BaseDisplayManager):
    """ Менеджер под SSD1306 (1-бит, 8×8, узкий статус-бар) """
    def __init__(self, driver, profile: OledProfile):
        super().__init__(driver, profile)
        self.statusbar = StatusBarMono8(self.profile.statusbar_icon, self.profile.image_mode)

class GrayDisplayManager(BaseDisplayManager):
    """ Менеджер под SSD1327 (RGB → 4-бит серый, 16×16, широкий статус-бар) """
    def __init__(self, driver, profile: OledProfile):
        super().__init__(driver, profile)
        self.statusbar = StatusBarGray16(self.profile.statusbar_icon, self.profile.image_mode)

def _detect_profile_name(driver, forced: str | None) -> str:
    if forced:
        return forced
    name = driver.__class__.__name__.lower()
    if "1327" in name:
        return "ssd1327"
    if "1306" in name:
        return "ssd1306"
    # эвристика по высоте
    return "ssd1327" if getattr(driver, "height", 64) >= 96 else "ssd1306"

def make_display_manager(driver, profile_name: str | None = None):
    # приоритет: явный аргумент -> env OLED_PROFILE -> эвристика
    forced = profile_name or os.getenv("OLED_PROFILE")
    prof_key = _detect_profile_name(driver, forced)
    profile = PROFILES[prof_key]

    if prof_key == "ssd1306":
        return MonoDisplayManager(driver, profile)
    else:
        return GrayDisplayManager(driver, profile)
