#!/usr/bin/env python3
import re, os
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid

class NetworkScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        cap_env = os.getenv("OLED_NET_CAP_MBPS")
        try:
            self.cap_bps = float(cap_env) * 1024 * 1024 if cap_env else 10 * 1024 * 1024.0
        except Exception:
            self.cap_bps = 10 * 1024 * 1024.0

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
        m = re.match(r'^([0-9]+(?:\.[0-9]+)?)([km]?)$', s)
        
        if not m:
            return 0.0
        
        val = float(m.group(1))
        unit = m.group(2)
        
        if unit == 'm': val *= 1024 * 1024
        elif unit == 'k': val *= 1024
        return val

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip = stats.get('ip', 'N/A')
        wifi_on = bool(stats.get('status_wifi', False))
        thr = stats.get('network_throughput') or {}
        up_txt = thr.get('upload', '0K/s') or '0K/s'
        dn_txt = thr.get('download', '0K/s') or '0K/s'

        row = 0
        row = grid.text_row(cv, dm, row, self._ip_line(cv, dm, ip), font=dm.font_small, fill=c)
        row = grid.text_row(cv, dm, row, f"Wi-Fi {'ON' if wifi_on else 'OFF'}", font=dm.font_small, fill=c)

        both = f"↑{up_txt}  ↓{dn_txt}"

        row = grid.text_row(cv, dm, row, f"↑{up_txt}", font=dm.font_small, fill=c)
        up_v = max(0.0, min(1.0, self._rate_parse(up_txt) / self.cap_bps))
        row = grid.bar_row(cv, dm, row, up_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                        fg=c, bg=dm.theme.background, border=c)

        row = grid.text_row(cv, dm, row, f"↓{dn_txt}", font=dm.font_small, fill=c)
        dn_v = max(0.0, min(1.0, self._rate_parse(dn_txt) / self.cap_bps))
        row = grid.bar_row(cv, dm, row, dn_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                        fg=c, bg=dm.theme.background, border=c)

        dm.show()
