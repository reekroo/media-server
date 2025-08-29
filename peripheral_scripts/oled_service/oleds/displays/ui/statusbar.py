#!/usr/bin/env python3
from __future__ import annotations
import os, time
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw
from oleds.configs.oled_icons import ICON_DATA

def _icon8_to_image(name: str, size: int, mode: str, fg, bg) -> Image.Image:
    """
    Берём 8×8 bitmap из ICON_DATA и поднимаем до size×size (обычно 16×16).
    Если иконки нет — рисуем пустышку-рамку.
    """
    data = ICON_DATA.get(name)
    img = Image.new(mode if mode in ("1", "L", "RGB") else "RGB", (size, size), color=bg)
    draw = ImageDraw.Draw(img)
    if not data:
        # пустая рамка-плейсхолдер
        draw.rectangle((0, 0, size - 1, size - 1), outline=fg, width=1)
        return img

    scale = max(1, size // 8)
    off = (size - 8 * scale) // 2  # центрируем
    # в 8×8 битовой строке единицы — "зажжённые" пиксели
    for y, row in enumerate(data[:8]):
        for x in range(8):
            if (row >> (7 - x)) & 1:
                x0 = off + x * scale
                y0 = off + y * scale
                draw.rectangle((x0, y0, x0 + scale - 1, y0 + scale - 1), fill=fg)
    return img

class StatusBar16:
    """
    Статус-бар под SSD1327: 16px иконки слева, часы справа.
    """
    def __init__(self, icon_order: Optional[List[str]] = None):
        env = os.getenv("OLED_STATUSBAR_ICONS", "").strip()
        if env:
            icon_order = [t.strip().lower() for t in env.split(",") if t.strip()]
        self.icon_order = icon_order or ["nvme", "ssd", "wifi", "docker"]

    def _state_icons(self, stats: Dict) -> List[str]:
        # NVMe
        nvme_ok = bool(stats.get("status_storage_disk", True))
        nvme_temp = stats.get("nvme_temp")
        try:
            if nvme_temp is not None and float(nvme_temp) >= 70.0:
                nvme_ok = False
        except Exception:
            pass
        nvme = "NVME_OK" if nvme_ok else "NVME_FAIL"

        # SSD (/)
        ssd_ok = bool(stats.get("status_root_disk", True))
        ssd = "STORAGE_OK" if ssd_ok else "STORAGE_FAIL"

        # Wi-Fi
        wifi_ok = bool(stats.get("status_wifi", False))
        wifi = "WIFI_OK" if wifi_ok else "WIFI_FAIL"

        # Docker
        dock_ok = bool(stats.get("status_docker", False))
        docker = "DOCKER_OK" if dock_ok else "DOCKER_FAIL"

        mapping = {
            "nvme": nvme,
            "ssd": ssd,
            "wifi": wifi,
            "docker": docker,
        }
        return [mapping[k] for k in self.icon_order if k in mapping]

    def draw(self, dm, stats: Dict):
        # Геометрия бара
        h = getattr(dm, "statusbar_height", 16)
        w = dm.width
        bg = dm.theme.background
        fg = dm.color()

        # фон + разделительная линия
        dm.draw.rectangle((0, 0, w - 1, h - 1), fill=bg)
        dm.draw.line((0, h - 1, w - 1, h - 1), fill=fg)

        # часы справа
        clock = time.strftime("%H:%M")
        tw = dm.draw.textlength(clock, font=dm.font_small)
        pad = 2
        tx = max(pad, w - pad - int(tw))
        # аккуратно выравниваем по вертикали (на середину бара)
        try:
            bbox = dm.font_small.getbbox("Ag")
            th = bbox[3] - bbox[1]
        except Exception:
            th = getattr(dm.font_small, "size", 12)
        ty = max(0, (h - th) // 2)
        dm.draw.text((tx, ty), clock, font=dm.font_small, fill=fg)

        # зона под иконки: всё, что осталось слева от часов - 2 px
        right_limit = tx - pad
        x = pad
        y = max(0, (h - 16) // 2)
        icons = self._state_icons(stats)

        # рисуем, пока помещаются
        for name in icons:
            if x + 16 > right_limit:
                break
            im = _icon8_to_image(name, 16, dm.image.mode, fg=fg, bg=bg)
            dm.image.paste(im, (x, y))
            x += 16 + 2  # 2px интервал
