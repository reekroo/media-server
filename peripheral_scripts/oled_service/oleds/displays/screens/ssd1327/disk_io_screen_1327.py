#!/usr/bin/env python3
import os
import re
from collections import deque

from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G


class DiskIOScreen1327(BaseScreen):
    """
    Disk I/O (SSD1327):
      • Заголовок
      • Текущие скорости: "R 2.4M/s   W 320K/s"
      • ОДНА объединённая область тренда (2 ряда): overlay из двух спарк-линий
          - Read:  серым
          - Write: белым (цвет темы)
      • История со сглаживанием EMA и автоподстройкой шкалы с затуханием
    """
    HANDLES_BACKGROUND = True

    def __init__(self):
        # История и сглаживание
        self._r_hist = deque(maxlen=120)
        self._w_hist = deque(maxlen=120)
        self._ema_r = None
        self._ema_w = None
        self._scale_bps = 1.0
        try:
            self._alpha = float(os.getenv("OLED_IO_EMA_ALPHA", "0.3"))   # EMA (0..1)
        except Exception:
            self._alpha = 0.3
        try:
            self._decay = float(os.getenv("OLED_IO_TREND_DECAY", "0.90"))  # коэффициент затухания шкалы
        except Exception:
            self._decay = 0.90

    # -------- helpers --------
    @staticmethod
    def _rate_parse(s: str) -> float:
        """ '320K/s' | '2.4M/s' | '500K' | '123456' -> bytes/s """
        if s is None:
            return 0.0
        if isinstance(s, (int, float)):
            return max(0.0, float(s))
        s = str(s).strip().lower().replace("/s", "")
        m = re.match(r"^([0-9]+(?:\.[0-9]+)?)([km]?)$", s)
        if not m:
            # если пришло '123456B' или что-то иное — вытащим число как есть
            try:
                return max(0.0, float(re.sub(r"[^0-9.]", "", s) or 0.0))
            except Exception:
                return 0.0
        val = float(m.group(1))
        unit = m.group(2)
        if unit == "m":
            val *= 1024 * 1024
        elif unit == "k":
            val *= 1024
        return max(0.0, val)

    @staticmethod
    def _fmt_bps(bps: float) -> str:
        if bps >= 1024 * 1024:
            return f"{bps / (1024 * 1024):.1f}M/s"
        return f"{bps / 1024:.0f}K/s"

    @staticmethod
    def _grey_color(dm, level=160):
        mode = getattr(dm.image, "mode", "L") if getattr(dm, "image", None) is not None else "L"
        level = int(max(0, min(255, level)))
        if mode == "L":
            return level
        if mode == "1":
            return 1
        return (level, level, level)

    # -------- draw --------
    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        # данные
        dio = stats.get("disk_io") or {}
        r_txt = (dio.get("read")  or "0K/s")
        w_txt = (dio.get("write") or "0K/s")

        r_bps = self._rate_parse(r_txt)
        w_bps = self._rate_parse(w_txt)

        # заголовок
        row = 0
        row = G.text_row(cv, dm, row, "Disk I/O", font=dm.font_small, fill=c)

        # текущие значения (одной строкой)
        line = f"R {self._fmt_bps(r_bps)}   W {self._fmt_bps(w_bps)}"
        row = G.text_row(cv, dm, row, line, font=dm.font, fill=c)

        # EMA сглаживание и история
        a = max(0.0, min(1.0, self._alpha))
        if self._ema_r is None: self._ema_r = r_bps
        if self._ema_w is None: self._ema_w = w_bps
        self._ema_r = a * r_bps + (1.0 - a) * self._ema_r
        self._ema_w = a * w_bps + (1.0 - a) * self._ema_w

        self._r_hist.append(self._ema_r)
        self._w_hist.append(self._ema_w)

        # Автошкала с затуханием
        local_max = max(max(self._r_hist or [0.0]), max(self._w_hist or [0.0]), 1.0)
        self._scale_bps = max(local_max, self._scale_bps * self._decay)

        def _norm(seq):
            s = max(self._scale_bps, 1.0)
            return [min(100.0, v * 100.0 / s) for v in seq]

        r_norm = _norm(self._r_hist)
        w_norm = _norm(self._w_hist)

        # объединённая спарк-область (2 ряда): Read серым, Write белым
        row = G.spark_area(
            cv, dm, row,
            series_list=[r_norm, w_norm],
            colors=[self._grey_color(dm, 160), c],
            height=max(12, G.base_lh(dm) * 2 - 4),
            gap_above=2, gap_below=0, min_rows=2
        )

        dm.show()
