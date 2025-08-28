#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capabilities:
    """ Возможности рендера и UX для конкретного дисплея """
    supports_gray: bool
    supports_animation: bool
    supports_charts: bool
    target_fps: int = 10  # ориентир для анимаций


# простейший отрисовщик "полос" и спарклайнов (без numpy)
class Charts:
    @staticmethod
    def bar(draw, x, y, w, h, value01: float, fg, bg=None, border_fg=None):
        value01 = max(0.0, min(1.0, value01))
        if bg is not None:
            draw.rectangle((x, y, x+w, y+h), fill=bg)
        if border_fg is not None:
            draw.rectangle((x, y, x+w, y+h), outline=border_fg, width=1)
        fill_w = max(0, int((w-2) * value01))
        draw.rectangle((x+1, y+1, x+1+fill_w, y+h-1), fill=fg)

    @staticmethod
    def sparkline(draw, x, y, w, h, values, fg):
        if not values:
            return
        n = len(values)
        if n == 1:
            draw.line((x, y+h//2, x+w, y+h//2), fill=fg)
            return
        vmin = min(values); vmax = max(values); rng = (vmax - vmin) or 1.0
        step = w / (n - 1)
        pts = []
        for i, v in enumerate(values):
            px = x + int(i * step)
            py = y + int(h - 1 - ((v - vmin) / rng) * (h - 1))
            pts.append((px, py))
        draw.line(pts, fill=fg, width=1)
