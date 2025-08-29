#!/usr/bin/env python3
import os
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
from ...ui import format as F
from ...ui.trend import Trend

class NetworkScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        alpha = float(os.getenv("OLED_NET_EMA_ALPHA", "0.3"))
        decay = float(os.getenv("OLED_NET_TREND_DECAY", "0.90"))
        self.trend = Trend(n_series=2, history=120, alpha=alpha, decay=decay)

    def _grey(self, dm, level=160):
        mode = getattr(dm.image, "mode", "L") if getattr(dm, "image", None) is not None else "L"
        level = int(max(0, min(255, level)))
        if mode == "L":  return level
        if mode == "1":  return 1
        return (level, level, level)

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip = stats.get("ip", "N/A")
        wifi = stats.get("status_wifi_connected", None)
        lan  = stats.get("status_lan", None)
        bt   = stats.get("status_bluetooth", None)

        thr = stats.get("network_throughput") or {}
        up_bps = F.parse_rate_bps(thr.get("upload"))
        dn_bps = F.parse_rate_bps(thr.get("download"))

        row = 0
        ip_line = F.fit_text(cv, dm.font_small, [f"IP {ip}", F.short_ip(ip)]) if hasattr(F, "fit_text") else (f"IP {ip}" if cv.draw.textlength(f"IP {ip}", font=dm.font_small) <= cv.width else F.short_ip(ip))

        row = G.text_row(cv, dm, row, ip_line, font=dm.font_small, fill=c)
        # Статусы (каждый на своей строке)
        def st(name, v): return f"{name} " + ("ON" if v is True else "OFF" if v is False else "N/A")
        row = G.text_row(cv, dm, row, st("WiFi", wifi), font=dm.font_small, fill=c)
        row = G.text_row(cv, dm, row, st("LAN",  lan),  font=dm.font_small, fill=c)
        row = G.text_row(cv, dm, row, st("BT",   bt),   font=dm.font_small, fill=c)

        rates = f"↑{F.fmt_bps(up_bps)}  ↓{F.fmt_bps(dn_bps)}"
        row = G.text_row(cv, dm, row, rates, font=dm.font, fill=c)

        up_norm, dn_norm = self.trend.update([up_bps, dn_bps])
        row = G.spark_area(
            cv, dm, row,
            series_list=[up_norm, dn_norm],
            colors=[self._grey(dm, 160), c],
            height=max(12, G.base_lh(dm) * 2 - 4),
            gap_above=2, gap_below=0, min_rows=2
        )

        dm.show()
