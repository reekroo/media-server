#!/usr/bin/env python3
from __future__ import annotations
import time
import logging
from typing import Dict, Tuple, Optional

from .ssd1327_configs import BarConfig
from .ssd1327_utils import text_y_center, icon_image, choose_icon_name
from oleds.widgets.batteries.battery import draw_battery

log = logging.getLogger(__name__)

class StatusBarSSD1327:

    def __init__(self, fg: int = 255, bg: int = 0, config: BarConfig | None = None):
        if abs(fg - bg) < 80:
            fg = 255 if bg < 128 else 0
        
        self.fg = int(fg)
        self.bg = int(bg)
        self.cfg = config or BarConfig()
        self.bar_h = self.cfg.pad_top + self.cfg.elem_h + self.cfg.pad_bot

    def draw(self, dm, stats: Dict) -> None:
        self.render(dm, stats)

    def drow_bar(self, dm) -> None:
        y1 = self.bar_h - 1
        dm.draw.line((0, y1, dm.image.size[0]-1, y1), fill=self.fg)

    def dwor_clock(self, dm, y: int, right_edge: int) -> Tuple[int,int,int]:
        text = time.strftime(self.cfg.clock_fmt)
        tw = int(dm.draw.textlength(text, font=dm.font))
        tx = right_edge - tw
        ty = text_y_center(dm.font, y, self.cfg.elem_h)
        dm.draw.text((tx, ty), text, font=dm.font, fill=self.fg)
        return tx, ty, tw

    def drow_battery(self, dm, y: int, right_edge: int) -> Tuple[int,int,int,int]:
        h = max(12, self.cfg.elem_h - 2)
        w = self.cfg.battery_width
        bx = right_edge - w
        by = y
        try:
            # Вызываем нашу функцию, она сама управляет цветами
            draw_battery(dm.draw, bx, by, w=w, h=h)
        except Exception as e:
            # Если что-то пойдет не так, мы увидим ошибку в логе, а не пустую батарею
            log.error(f"CRITICAL: Battery widget failed to draw: {e}", exc_info=True)
            # Рисуем крест как индикатор ошибки
            dm.draw.line((bx, by, bx + w, by + h), fill=self.fg)
            dm.draw.line((bx, by + h, bx + w, by), fill=self.fg)
        return bx, by, w, h

    def _draw_icon(self, dm, name: Optional[str], x: int, y: int) -> int:
        if not name:
            return x
        im = icon_image(name, self.cfg.elem_h, dm.image.mode, self.fg, self.bg)
        if im:
            dm.image.paste(im, (x, y))
            x += self.cfg.elem_h + self.cfg.gap
        return x

    def drow_storage_status(self, dm, stats: Dict, x: int, y: int) -> int:
        ok = bool(stats.get("status_root_disk", True))
        name = choose_icon_name("storage", ok)
        return self._draw_icon(dm, name, x, y)

    def drow_nwme_status(self, dm, stats: Dict, x: int, y: int) -> int:
        ok = bool(stats.get("status_nvme", False))
        if "nvme_power_ok" in stats:
            try: ok = ok and bool(stats["nvme_power_ok"])
            except Exception: pass
        name = choose_icon_name("nvme", ok)
        return self._draw_icon(dm, name, x, y)

    def drow_bluetooth_status(self, dm, stats: Dict, x: int, y: int) -> int:
        ok = bool(stats.get("status_bluetooth", False))
        name = choose_icon_name("bluetooth", ok)
        return self._draw_icon(dm, name, x, y)

    def drow_wifi_status(self, dm, stats: Dict, x: int, y: int) -> int:
        ok = bool(stats.get("status_wifi", False))
        name = choose_icon_name("wifi", ok)
        return self._draw_icon(dm, name, x, y)

    def drow_docker_status(self, dm, stats: Dict, x: int, y: int) -> int:
        ok = bool(stats.get("status_docker", False))
        name = choose_icon_name("docker", ok)
        return self._draw_icon(dm, name, x, y)

    def render(self, dm, stats: Dict) -> None:
        W, _ = dm.image.size
        y_elem = self.cfg.pad_top
        left_x = 0
        right_edge = W
        
        tx, _, tw = self.dwor_clock(dm, y_elem, right_edge)
        bx, _, bw, _ = self.drow_battery(dm, y_elem, tx - self.cfg.right_gap_between)
        left_limit = bx - self.cfg.gap

        needed_per_icon = self.cfg.elem_h + self.cfg.gap
        max_icons = len(self.cfg.left_icons)
        
        x = left_x
        for idx, cat in enumerate(self.cfg.left_icons):
            width_if_place = self.cfg.elem_h + (self.cfg.gap if idx < max_icons - 1 else 0)
            if x + width_if_place > left_limit:
                break
            if cat == "storage":
                x = self.drow_storage_status(dm, stats, x, y_elem)
            elif cat == "nvme":
                x = self.drow_nwme_status(dm, stats, x, y_elem)
            elif cat == "bluetooth":
                x = self.drow_bluetooth_status(dm, stats, x, y_elem)
            elif cat == "wifi":
                x = self.drow_wifi_status(dm, stats, x, y_elem)
            elif cat == "docker":
                x = self.drow_docker_status(dm, stats, x, y_elem)

        self.drow_bar(dm)