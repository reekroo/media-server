#!/usr/bin/env python3
import re
from collections import deque
from ..base import BaseScreen
from ...ui.canvas import Canvas

class DiskIOScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self._r_hist = deque(maxlen=60)
        self._w_hist = deque(maxlen=60)

    def _parse_rate(self, s: str) -> float:
        # "320K", "2.4M" -> bytes/s (провайдер отдаёт без '/s'; считаем, что это за интервал update)
        if not s: return 0.0
        m = re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)\s*([kKmM])?\s*$', s)
        if not m: return 0.0
        val = float(m.group(1)); unit = (m.group(2) or '').lower()
        if unit == 'm': return val * 1024 * 1024
        if unit == 'k': return val * 1024
        return val

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        io = stats.get('disk_io', {'read':'0K', 'write':'0K'}) or {}
        r_txt, w_txt = io.get('read','0K'), io.get('write','0K')

        r_b = self._parse_rate(r_txt)
        w_b = self._parse_rate(w_txt)
        self._r_hist.append(r_b)
        self._w_hist.append(w_b)

        cap = 20 * 1024 * 1024.0  # 20 MB/s шкала
        v_r = max(0.0, min(1.0, r_b / cap))
        v_w = max(0.0, min(1.0, w_b / cap))

        row = 0
        row = cv.text_row(row, f"Read   {r_txt}/s", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 10, v_r, fg=c, bg=dm.theme.background, border=c)
        row += 1
        row = cv.text_row(row, f"Write  {w_txt}/s", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 10, v_w, fg=c, bg=dm.theme.background, border=c)

        # двойная спарклиния (R / W) снизу
        y_spark = min(cv.bottom - 12, cv.top + row*Canvas._line_height(dm.font) + 4)
        cv.sparkline(cv.left, y_spark, min(120, cv.width), 12, list(self._r_hist), fg=c)
        cv.sparkline(cv.left, y_spark+6, min(120, cv.width), 12, list(self._w_hist), fg=c)

        dm.show()
