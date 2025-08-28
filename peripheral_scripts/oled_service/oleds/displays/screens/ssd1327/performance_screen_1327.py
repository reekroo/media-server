#!/usr/bin/env python3
import math
from collections import deque
from ..base import BaseScreen
from ...ui.canvas import Canvas

class PerformanceScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self._t = 0
        self._cpu_hist = deque(maxlen=60)

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)

        cv = Canvas.from_display(dm)

        ip   = stats.get('ip', 'N/A')
        cpu  = float(stats.get('cpu', 0) or 0.0)
        temp = float(stats.get('temp', 0) or 0.0)
        freq = float(stats.get('cpu_freq', 0) or 0.0)
        mem  = stats.get('mem', {}) or {}
        swap = stats.get('swap', {}) or {}

        def gb(b): return f"{(b or 0)/(1024**3):.1f}G"

        row = 0
        row = cv.text_row(row, f"IP {ip}", font=dm.font_small, fill=c)
        row = cv.text_row(row, f"CPU {cpu:>3.0f}%  {freq/1000:.1f}GHz  {temp:.0f}C", font=dm.font, fill=c)
        row = cv.text_row(row, f"MEM {gb(mem.get('used'))}/{gb(mem.get('total'))}  {mem.get('percent',0):.0f}%", font=dm.font, fill=c)
        row = cv.text_row(row, f"SWP {gb(swap.get('used'))}/{gb(swap.get('total'))}  {swap.get('percent',0):.0f}%", font=dm.font, fill=c)

        # CPU bar + sparkline
        bar_w = min(120, cv.width)
        bar_h = 12
        bar_x = cv.left
        bar_y = min(cv.bottom - (bar_h + 16), cv.top + row * Canvas._line_height(dm.font) + 4)

        pulse = 0.95 + 0.05 * math.sin(self._t * 2*math.pi / 30.0)
        value01 = max(0.0, min(1.0, (cpu/100.0) * pulse))

        cv.bar(bar_x, bar_y, bar_w, bar_h, value01=value01, fg=c, bg=dm.theme.background, border=c)

        self._cpu_hist.append(cpu)
        cv.sparkline(bar_x, min(bar_y + bar_h + 4, cv.bottom - 12), bar_w, 12, list(self._cpu_hist), fg=c)

        self._t = (self._t + 1) % 10000
        dm.show()
