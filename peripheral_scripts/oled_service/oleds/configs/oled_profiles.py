#!/usr/bin/env python3
from dataclasses import dataclass
import os
from pathlib import Path

def _default_font_path():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return ""

@dataclass(frozen=True)
class OledProfile:
    name: str
    width: int
    height: int
    image_mode: str           # "1" or "RGB" (for SSD1327)
    statusbar_icon: int       # px (8 or 16)
    font_small: int
    font_regular: int
    font_large: int
    font_path: str

def _envint(key, default):
    try:
        return int(os.getenv(key, str(default)))
    except:
        return default

SSD1306_PROFILE = OledProfile(
    name="ssd1306",
    width=_envint("OLED_WIDTH", 128),
    height=_envint("OLED_HEIGHT", 64),
    image_mode="1",
    statusbar_icon=8,
    font_small=_envint("OLED_FONT_SMALL", 10),
    font_regular=_envint("OLED_FONT_REGULAR", 12),
    font_large=_envint("OLED_FONT_LARGE", 14),
    font_path=os.getenv("OLED_FONT_PATH", _default_font_path()),
)

SSD1327_PROFILE = OledProfile(
    name="ssd1327",
    width=_envint("OLED_WIDTH", 128),
    height=_envint("OLED_HEIGHT", 128),
    image_mode=os.getenv("OLED_IMAGE_MODE", "RGB"),
    statusbar_icon=16,
    font_small=_envint("OLED_FONT_SMALL", 10),
    font_regular=_envint("OLED_FONT_REGULAR", 12),
    font_large=_envint("OLED_FONT_LARGE", 14),
    font_path=os.getenv("OLED_FONT_PATH", _default_font_path()),
)

PROFILES = {
    "ssd1306": SSD1306_PROFILE,
    "ssd1327": SSD1327_PROFILE,
}
