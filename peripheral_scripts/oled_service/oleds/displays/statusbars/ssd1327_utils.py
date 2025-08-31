#!/usr/bin/env python3
from __future__ import annotations
from typing import List, Optional
from PIL import Image, ImageDraw

try:
    from oleds.models.icons_x16 import ICON_DATA as ICON16
except Exception:
    ICON16 = {}

from oleds.models.icons_x8 import ICON_DATA as ICON8

def choose_icon_name(category: str, ok: Optional[bool]) -> Optional[str]:
    bank = {
        "nvme":      ["NVME_OK", "NVME_FAIL", "NVME"],
        "storage":   ["STORAGE_OK", "STORAGE_FAIL", "SSD", "DISK", "ROOT"],
        "wifi":      ["WIFI_OK", "WIFI_FAIL", "WIFI"],
        "docker":    ["DOCKER_OK", "DOCKER_FAIL", "DOCKER", "CONTAINER"],
        "bluetooth": ["BT_OK", "BT_FAIL", "BT", "BLUETOOTH"],
    }

    cands = bank.get(category, [])
    pri: List[str] = []
    
    if ok is True:
        pri += [n for n in cands if n.endswith("_OK")]
    elif ok is False:
        pri += [n for n in cands if n.endswith("_FAIL")]
    pri += [n for n in cands if not (n.endswith("_OK") or n.endswith("_FAIL"))]
    for name in pri:
        if name in ICON16 or name in ICON8:
            return name
    return None

def bitmap_to_img(bitmap: List[int], size: int, mode: str, fg: int, bg: int) -> Image.Image:
    img = Image.new(mode if mode in ("1","L","RGB") else "RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    grid = 16 if size >= 16 and len(bitmap) == 16 else 8
    scale = max(1, size // grid)
    ox = (size - grid * scale) // 2
    oy = (size - grid * scale) // 2

    for y, row in enumerate(bitmap[:grid]):
        for x in range(grid):
            if row & (1 << (grid - 1 - x)):
                x0 = ox + x * scale
                y0 = oy + y * scale
                x1 = x0 + scale - 1
                y1 = y0 + scale - 1
                d.rectangle((x0, y0, x1, y1), fill=fg)
    
    return img

def icon_image(name: str, size: int, mode: str, fg: int, bg: int) -> Optional[Image.Image]:
    if name in ICON16:
        return bitmap_to_img(ICON16[name], size, mode, fg, bg)
    if name in ICON8:
        return bitmap_to_img(ICON8[name], size, mode, fg, bg)
    return None

def text_y_center(font, y_top: int, box_h: int) -> int:
    try:
        x0,y0,x1,y1 = font.getbbox("0")
        h = y1 - y0
        return y_top + (box_h - h)//2 - y0

    except Exception:
        sz = getattr(font, "size", 12)
        return y_top + (box_h - sz)//2