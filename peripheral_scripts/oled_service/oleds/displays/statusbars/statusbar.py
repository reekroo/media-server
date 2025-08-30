#!/usr/bin/env python3
from __future__ import annotations
import time
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw

from oleds.models.icons_x8 import ICON_DATA
from oleds.widgets.battery import draw_battery  # читает /run/peripherals/ups/status.json

BAR_H_DEFAULT = 20 
PAD = 2

# ---------- утилиты ----------


# def _icon8_to_image(name: str, size: int, mode: str, fg, bg) -> Image.Image:

#     data = ICON_DATA.get(name)
#     img = Image.new(mode if mode in ("1", "L", "RGB") else "RGB", (size, size), color=bg)
#     draw = ImageDraw.Draw(img)
#     if not data:
#         draw.rectangle((0, 0, size - 1, size - 1), outline=fg, width=1)
#         return img

#     scale = max(1, size // 8)
#     off = (size - 8 * scale) // 2
#     for y, row in enumerate(data[:8]):
#         for x in range(8):
#             if (row >> (7 - x)) & 1:
#                 x0 = off + x * scale
#                 y0 = off + y * scale
#                 draw.rectangle((x0, y0, x0 + scale - 1, y0 + scale - 1), fill=fg)
#     return img


def _icon8_to_image(name: str, size: int, mode: str, fg, bg) -> Image.Image:
    """
    Рисует 8x8 битовую иконку в квадрат size x size (по факту пиксели 8x8).
    """
    data = ICON_DATA.get(name)
    img = Image.new(mode if mode in ("1", "L", "RGB") else "RGB", (size, size), color=bg)
    draw = ImageDraw.Draw(img)
    if not data:
        draw.rectangle((0, 0, size - 1, size - 1), outline=fg, width=1)
        return img
    for y, row in enumerate(data[:size]):
        byte = row
        for x in range(8):
            if byte & (1 << (7 - x)):
                draw.point((x, y), fill=fg)
    return img

def _text_vcenter_y(draw_font, text: str, bar_top: int, bar_h: int) -> int:
    """
    Центрирует текст по вертикали в полосе бара с учётом bbox.
    """
    try:
        x0, y0, x1, y1 = draw_font.getbbox(text)
        h = y1 - y0
        return bar_top + (bar_h - h) // 2 - y0
    except Exception:
        sz = getattr(draw_font, "size", 12)
        return bar_top + (bar_h - sz) // 2

# ---------- сам класс бара ----------

class StatusBar16:
    """
    Верхний статус-бар.
      - слева: иконки (NVMe, storage, Wi-Fi, Docker)
      - справа: часы
      - между ними: батарейка (UPS)
    Интерфейс дисплея зовёт: StatusBar16.draw(dm, stats)
    """

    def __init__(self, fg=255, bg=0):
        self.fg = fg
        self.bg = bg

    # публичный вход
    def draw(self, dm, stats: Dict) -> None:
        """
        dm: объект дисплея с полями image (PIL.Image), draw (ImageDraw), font_small
        stats: словарь статусов (status_nvme, status_root_disk, status_wifi, status_docker, …)
        """
        w, _ = dm.image.size
        bar_h = getattr(dm, "status_bar_height", BAR_H_DEFAULT)
        y_top = 0

        # 1) полоса/разделитель
        self.drow_bar(dm, y_top, bar_h)

        # 2) часы (справа), координаты возвращаем чтобы знать границу
        tx, ty, tw = self.dwor_clock(dm, y_top, bar_h)

        # 3) батарейка — вставляем слева от часов
        bx, by, bat_w, bat_h = self.drow_battery(dm, tx, y_top, bar_h)

        # 4) иконки слева до правой границы (bx - PAD)
        right_limit = bx - PAD
        x = PAD
        y = y_top + max(0, (bar_h - 16) // 2)

        x = self.drow_nwme_status(dm, stats, x, y, right_limit)
        x = self.drow_storage_status(dm, stats, x, y, right_limit)
        x = self.drow_wifi_status(dm, stats, x, y, right_limit)
        _ = self.drow_docker_status(dm, stats, x, y, right_limit)

    # ---------- части бара (имена как просили) ----------

    def drow_bar(self, dm, y_top: int, bar_h: int) -> None:
        """
        Рисует само «полотно» бара: 1-px разделитель по нижней кромке.
        """
        y1 = y_top + bar_h
        dm.draw.line((0, y1 - 1, dm.image.size[0] - 1, y1 - 1), fill=self.fg)

    def dwor_clock(self, dm, y_top: int, bar_h: int) -> Tuple[int, int, int]:
        """
        Рисует часы справа. Возвращает (tx, ty, tw).
        """
        clock = time.strftime("%H:%M")
        tw = dm.draw.textlength(clock, font=dm.font)
        tx = max(PAD, dm.image.size[0] - PAD - int(tw))
        ty = _text_vcenter_y(dm.font, clock, y_top, bar_h)
        dm.draw.text((tx, ty), clock, font=dm.font, fill=self.fg)
        return tx, ty, int(tw)

    def drow_battery(self, dm, tx_right: int, y_top: int, bar_h: int) -> Tuple[int, int, int, int]:
        """
        Рисует батарейку слева от часов. Возвращает её (bx, by, w, h).
        """
        bat_h = max(10, min(12, bar_h - 4))
        bat_w = max(22, int(bat_h * 2.2))
        bx = max(PAD, tx_right - PAD - bat_w)
        by = y_top + (bar_h - bat_h) // 2
        try:
            draw_battery(dm.draw, bx, by, w=bat_w, h=bat_h)
        except Exception:
            # если статус не доступен — «дырка» без падения
            pass
        return bx, by, bat_w, bat_h

    def drow_nwme_status(self, dm, stats: Dict, x: int, y: int, right_limit: int) -> int:
        """
        Рисует NVMe-статус (иконка 16x16). Возвращает новый x.
        """
        if x + 16 > right_limit:
            return x
        nvme_ok = bool(stats.get("status_nvme", False))
        if "nvme_power_ok" in stats:
            try:
                nvme_ok = nvme_ok and bool(stats["nvme_power_ok"])
            except Exception:
                pass
        name = "NVME_OK" if nvme_ok else "NVME_FAIL"
        if name in ICON_DATA:
            im = _icon8_to_image(name, 16, dm.image.mode, self.fg, self.bg)
            dm.image.paste(im, (x, y))
            x += 16 + 2
        return x

    def drow_storage_status(self, dm, stats: Dict, x: int, y: int, right_limit: int) -> int:
        """
        Рисует статус системного диска (root storage).
        """
        if x + 16 > right_limit:
            return x
        ok = bool(stats.get("status_root_disk", True))
        name = "STORAGE_OK" if ok else "STORAGE_FAIL"
        if name in ICON_DATA:
            im = _icon8_to_image(name, 16, dm.image.mode, self.fg, self.bg)
            dm.image.paste(im, (x, y))
            x += 16 + 2
        return x

    def drow_wifi_status(self, dm, stats: Dict, x: int, y: int, right_limit: int) -> int:
        """
        Рисует Wi-Fi статус.
        """
        if x + 16 > right_limit:
            return x
        ok = bool(stats.get("status_wifi", False))
        name = "WIFI_OK" if ok else "WIFI_FAIL"
        if name in ICON_DATA:
            im = _icon8_to_image(name, 16, dm.image.mode, self.fg, self.bg)
            dm.image.paste(im, (x, y))
            x += 16 + 2
        return x

    def drow_docker_status(self, dm, stats: Dict, x: int, y: int, right_limit: int) -> int:
        """
        Рисует Docker статус.
        """
        if x + 16 > right_limit:
            return x
        ok = bool(stats.get("status_docker", False))
        name = "DOCKER_OK" if ok else "DOCKER_FAIL"
        if name in ICON_DATA:
            im = _icon8_to_image(name, 16, dm.image.mode, self.fg, self.bg)
            dm.image.paste(im, (x, y))
            x += 16 + 2
        return x
