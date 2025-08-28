#!/usr/bin/env python3
import re
from ..base import BaseScreen
from ...ui.canvas import Canvas

class NetworkScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def _parse_speed(self, s: str) -> float:
        # "320K/s", "2.4M/s" -> bytes/s
        if not s: return 0.0
        m = re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)\s*([kKmM])?/?s?\s*$', s)
        if not m: return 0.0
        val = float(m.group(1))
        unit = (m.group(2) or '').lower()
        if unit == 'm': return val * 1024 * 1024
        if unit == 'k': return val * 1024
        return val

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip = stats.get('ip', 'N/A')
        wifi_on = bool(stats.get('status_wifi', False))
        thr = stats.get('network_throughput', {'upload':'0K/s','download':'0K/s'}) or {}
        up_txt, down_txt = thr.get('upload','0K/s'), thr.get('download','0K/s')
        up_bps  = self._parse_speed(up_txt)
        down_bps= self._parse_speed(down_txt)

        cap = 10 * 1024 * 1024.0
        v_up = max(0.0, min(1.0, up_bps/cap))
        v_dn = max(0.0, min(1.0, down_bps/cap))

        row = 0
        row = cv.text_row(row, f"IP {ip}", font=dm.font_small, fill=c)
        row = cv.text_row(row, f"Wi-Fi: {'ON' if wifi_on else 'OFF'}", font=dm.font, fill=c)
        row = cv.text_row(row, f"↑ Upload {up_txt}", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 10, v_up, fg=c, bg=dm.theme.background, border=c)
        row += 1
        row = cv.text_row(row, f"↓ Download {down_txt}", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 10, v_dn, fg=c, bg=dm.theme.background, border=c)

        dm.show()
