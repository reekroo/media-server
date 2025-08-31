#!/usr/bin/env python3
from __future__ import annotations
import os

from oleds.configs.oled_profiles import PROFILES
from oleds.displays.ssd1306_manager import MonoDisplayManager
from oleds.displays.ssd1327_manager import GrayDisplayManager

def _detect_profile_name(driver, forced: str | None) -> str:
    if forced:
        name = forced.lower().strip()
        if name in PROFILES:
            return name
        if "1327" in name:
            return "ssd1327"
        if "1306" in name:
            return "ssd1306"

    ident = (getattr(driver, "identifier", "") or getattr(driver, "name", "")).lower()
    
    if "1327" in ident:
        return "ssd1327"
    if "1306" in ident:
        return "ssd1306"
    
    return "ssd1327" if getattr(driver, "height", 64) >= 96 else "ssd1306"

def make_display_manager(driver, profile_name: str | None = None):
    forced = profile_name or os.getenv("OLED_PROFILE")
    prof_key = _detect_profile_name(driver, forced)
    profile = PROFILES[prof_key]

    if prof_key == "ssd1306":
        return MonoDisplayManager(driver, profile)
    
    return GrayDisplayManager(driver, profile)