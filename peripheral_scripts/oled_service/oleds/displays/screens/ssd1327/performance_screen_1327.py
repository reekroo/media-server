#!/usr/bin/env python3
import math
from collections import deque
from ..base import BaseScreen

class PerformanceScreen1327(BaseScreen):
    def __init__(self):
        self._t = 0
        self._cpu_hist = deque(maxlen=60)

    def draw(self, dm, stats):
        c = dm.color()

        dm.begin(stats)
        dm.draw_status_bar(stats)

        ip   = stats.get('ip', 'N/A')
        cpu  = float(stats.get('cpu', 0) or 0.0)
        temp = float(stats.get('temp', 0) or 0.0)
        freq = float(stats.get('cpu_freq', 0) or 0.0)
        mem  = stats.get('mem', {}) or {}
        swap = stats.get('swap', {}) or {}

        def gb(b): return f"{(b or 0)/(1024**3):.1f}G"

        # Текстовые блоки
        dm.draw.text((4, 22), f"IP {ip}", font=dm.font_small, fill=c)
        dm.draw.text((4, 40), f"CPU {cpu:>3.0f}%  {freq/1000:.1f}GHz  {temp:.0f}C", font=dm.font, fill=c)
        dm.draw.text((4, 58), f"MEM {gb(mem.get('used'))}/{gb(mem.get('total'))}  {mem.get('percent',0):.0f}%", font=dm.font, fill=c)
        dm.draw.text((4, 76), f"SWP {gb(swap.get('used'))}/{gb(swap.get('total'))}  {swap.get('percent',0):.0f}%", font=dm.font, fill=c)

        # Безопасная полоска CPU (внутренняя ширина >=0)
        bar_x, bar_y, bar_w, bar_h = 4, 96, 120, 12
        # рамка
        dm.draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=c, width=1)

        # дыхание + кламп
        pulse = 0.95 + 0.05 * math.sin(self._t * 2*math.pi / 30.0)
        value01 = max(0.0, min(1.0, (cpu / 100.0) * pulse))

        inner_w = max(0, int(round((bar_w - 2) * value01)))  # только внутренность
        if inner_w > 0:
            x0 = bar_x + 1
            y0 = bar_y + 1
            x1 = x0 + inner_w - 1  # гарантированно x1 >= x0
            y1 = bar_y + bar_h - 1
            dm.draw.rectangle((x0, y0, x1, y1), fill=c)

        # История CPU (тонкая линия)
        self._cpu_hist.append(cpu)
        hist = list(self._cpu_hist)
        if len(hist) >= 2:
            # простая спарклиния на 120x12
            vmin = min(hist); vmax = max(hist); rng = (vmax - vmin) or 1.0
            step = (120 - 1) / (len(hist) - 1)
            pts = []
            for i, v in enumerate(hist):
                px = 4 + int(i * step)
                py = 112 + int(12 - 1 - ((v - vmin) / rng) * (12 - 1))
                pts.append((px, py))
            dm.draw.line(pts, fill=c, width=1)

        self._t = (self._t + 1) % 10000
        dm.show()
