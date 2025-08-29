#!/usr/bin/env python3
import os
import re
from collections import deque

from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid

class NetworkScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self._up_hist = deque(maxlen=120)
        self._dn_hist = deque(maxlen=120)
        self._ema_up = None
        self._ema_dn = None
        self._scale_bps = 1.0
        try:
            self._alpha = float(os.getenv("OLED_NET_EMA_ALPHA", "0.3"))
        except Exception:
            self._alpha = 0.3
        try:
            self._decay = float(os.getenv("OLED_NET_TREND_DECAY", "0.90"))
        except Exception:
            self._decay = 0.90

    def _ip_line(self, cv, dm, ip: str) -> str:
        full = f"IP {ip}"
        if cv.draw.textlength(full, font=dm.font_small) <= cv.width:
            return full
        try:
            parts = ip.split(".")
            return f"IP …{parts[-2]}.{parts[-1]}"
        except Exception:
            return "IP N/A"

    def _rate_parse(self, s: str) -> float:
        if not s:
            return 0.0
        s = s.strip().lower().replace("/s", "")
        m = re.match(r"^([0-9]+(?:\.[0-9]+)?)([km]?)$", s)
        if not m:
            return 0.0
        val = float(m.group(1))
        unit = m.group(2)
        if unit == "m":
            val *= 1024 * 1024
        elif unit == "k":
            val *= 1024
        return max(0.0, val)

    def _fmt_bps(self, bps: float) -> str:
        if bps >= 1024 * 1024:
            return f"{bps / (1024 * 1024):.1f}M/s"
        return f"{bps / 1024:.0f}K/s"

    def _fmt_status(self, name: str, val) -> str:
        if val is True:
            st = "ON"
        elif val is False:
            st = "OFF"
        else:
            st = "N/A"
        return f"{name} {st}"

    def _grey_color(self, dm, level=160):
        mode = getattr(dm.image, "mode", "L") if getattr(dm, "image", None) is not None else "L"
        level = int(max(0, min(255, level)))
        if mode == "L":
            return level
        if mode == "1":
            return 1
        return (level, level, level)

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip = stats.get("ip", "N/A")
        wifi_conn = stats.get("status_wifi_connected", None)
        lan_conn  = stats.get("status_lan", None)
        bt_en     = stats.get("status_bluetooth", None)

        thr = stats.get("network_throughput") or {}
        up_txt = (thr.get("upload") or "0K/s")
        dn_txt = (thr.get("download") or "0K/s")

        row = 0
        row = grid.text_row(cv, dm, row, self._ip_line(cv, dm, ip), font=dm.font_small, fill=c)
        row = grid.text_row(cv, dm, row, self._fmt_status("WiFi", wifi_conn), font=dm.font_small, fill=c)
        row = grid.text_row(cv, dm, row, self._fmt_status("LAN",  lan_conn),  font=dm.font_small, fill=c)
        row = grid.text_row(cv, dm, row, self._fmt_status("BT",   bt_en),     font=dm.font_small, fill=c)

        up_bps = self._rate_parse(up_txt)
        dn_bps = self._rate_parse(dn_txt)
        rates_line = f"↑{self._fmt_bps(up_bps)}  ↓{self._fmt_bps(dn_bps)}"

        row = grid.text_row(cv, dm, row, rates_line, font=dm.font, fill=c)

        a = max(0.0, min(1.0, self._alpha))
        if self._ema_up is None:
            self._ema_up = up_bps
        if self._ema_dn is None:
            self._ema_dn = dn_bps
        self._ema_up = a * up_bps + (1.0 - a) * self._ema_up
        self._ema_dn = a * dn_bps + (1.0 - a) * self._ema_dn

        self._up_hist.append(self._ema_up)
        self._dn_hist.append(self._ema_dn)

        local_max = max(max(self._up_hist or [0.0]), max(self._dn_hist or [0.0]), 1.0)
        self._scale_bps = max(local_max, self._scale_bps * self._decay)

        def _norm(seq):
            s = max(self._scale_bps, 1.0)
            return [min(100.0, v * 100.0 / s) for v in seq]

        up_norm = _norm(self._up_hist)
        dn_norm = _norm(self._dn_hist)

        row = grid.spark_area(
            cv, dm, row,
            series_list=[up_norm, dn_norm],
            colors=[self._grey_color(dm, 160), c],
            height=max(12, grid.base_lh(dm) * 2 - 4),
            gap_above=2, gap_below=0, min_rows=2
        )

        dm.show()
