#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageFont

from oleds.models.icons_x8 import ICON_DATA

def _default_font_path() -> str:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for p in candidates:
        if Path(p).exists():
            return p
    
    return ""

@dataclass(frozen=True)
class Theme:
    name: str
    image_mode: str                # "1" or "RGB" (for SSD1327)
    foreground: Tuple[int, ...]    # 255 or (255,255,255)
    background: Tuple[int, ...]    # 0 or (0,0,0)
    font_path: str
    font_small: int
    font_regular: int
    font_large: int
    statusbar_icon: int              # 8 - mono, 16 gray
    icon_pack: Optional[str] = None  # png icons (optional)

    def load_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        if self.font_path:
            try:
                return ImageFont.truetype(self.font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()


class IconProvider:
    def __init__(self, image_mode: str, size: int, icon_pack: Optional[str] = None):
        self.image_mode = image_mode
        self.size = size
        self.icon_pack = icon_pack

    def _try_load_png(self, name: str) -> Optional[Image.Image]:
        if not self.icon_pack:
            return None
        
        roots = [
            Path(__file__).resolve().parent.parent / "assets" / "icons" / self.icon_pack / f"{name}.png",
            Path(__file__).resolve().parent.parent / "assets" / "icons" / self.icon_pack / str(self.size) / f"{name}.png",
        ]

        for p in roots:
            if p.exists():
                try:
                    return Image.open(p).convert("RGBA")
                except Exception:
                    pass

        return None

    def get(self, name: str) -> Optional[Image.Image]:
        img = self._try_load_png(name)
        if img is not None:
            if img.size != (self.size, self.size):
                img = img.resize((self.size, self.size), Image.NEAREST)
            if self.image_mode == "1":
                img = img.convert("1")
            else:
                img = img.convert(self.image_mode)
            return img

        data = ICON_DATA.get(name)
        
        if not data:
            return None
        
        icon = Image.frombytes('1', (8, 8), bytes(data))
        
        if self.size != 8:
            icon = icon.resize((self.size, self.size), Image.NEAREST)
        
        if self.image_mode != '1':
            icon = icon.convert(self.image_mode)
        
        return icon

def make_mono_theme() -> Theme:
    return Theme(
        name="mono",
        image_mode="1",
        foreground=255,
        background=0,
        font_path=os.getenv("OLED_FONT_PATH", _default_font_path()),
        font_small=int(os.getenv("OLED_FONT_SMALL", "10")),
        font_regular=int(os.getenv("OLED_FONT_REGULAR", "12")),
        font_large=int(os.getenv("OLED_FONT_LARGE", "14")),
        statusbar_icon=8,
        icon_pack=os.getenv("OLED_ICON_PACK") or None,
    )

def make_gray_theme() -> Theme:
    return Theme(
        name="gray",
        image_mode=os.getenv("OLED_IMAGE_MODE", "RGB"),
        foreground=(255, 255, 255),
        background=(0, 0, 0),
        font_path=os.getenv("OLED_FONT_PATH", _default_font_path()),
        font_small=int(os.getenv("OLED_FONT_SMALL", "10")),
        font_regular=int(os.getenv("OLED_FONT_REGULAR", "12")),
        font_large=int(os.getenv("OLED_FONT_LARGE", "14")),
        statusbar_icon=16,
        icon_pack=os.getenv("OLED_ICON_PACK") or None,
    )

def get_theme(profile_name: str | None) -> Theme:
    forced = os.getenv("OLED_THEME")

    if forced:
        forced = forced.strip().lower()
        
        if forced in ("mono", "gray"):
            return make_gray_theme() if forced == "gray" else make_mono_theme()

    if profile_name == "ssd1327":
        return make_gray_theme()
    
    return make_mono_theme()