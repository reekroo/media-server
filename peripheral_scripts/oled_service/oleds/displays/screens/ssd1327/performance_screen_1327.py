#!/usr/bin/env python3
import math
from collections import deque
from ..base import BaseScreen

class PerformanceScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self._t = 0
        self._cpu_hist = deque(maxlen=60)

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)

        ip   = stats.get('ip', 'N/A')
        cpu  = float(stats.get('cpu', 0) or 0.0)
        temp = float(stats.get('temp', 0) or 0.0)
        freq = float(stats.get('cpu_freq', 0) or 0.0)
        mem  = stats.get('mem', {}) or {}
        swap = stats.get('swap', {}) or {}

        def gb(b): return f"{(b or 0)/(1024**3):.1f}G"

        row = 0
        row = dm.draw_text_row(row, f"IP {ip}", font=dm.font_small, fill=c)
        row = dm.draw_text_row(row, f"CPU {cpu:>3.0f}%  {freq/1000:.1f}GHz  {temp:.0f}C", font=dm.font, fill=c)
        row = dm.draw_text_row(row, f"MEM {gb(mem.get('used'))}/{gb(mem.get('total'))}  {mem.get('percent',0):.0f}%", font=dm.font, fill=c)
        row = dm.draw_text_row(row, f"SWP {gb(swap.get('used'))}/{gb(swap.get('total'))}  {swap.get('percent',0):.0f}%", font=dm.font, fill=c)

        # Полоса CPU — прижмём ниже текущей строки, но в пределах контента
        bar_w, bar_h = 120, 12
        bar_x = dm.content_left
        bar_y = min(dm.content_bottom - (bar_h + 16),  # оставим место для спарклайна
                    row + 4)
        dm.rect_safe((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=c, width=1)

        pulse = 0.95 + 0.05 * math.sin(self._t * 2*math.pi / 30.0)
        value01 = max(0.0, min(1.0, (cpu / 100.0) * pulse))
        inner_w = max(0, int(round((bar_w - 2) * value01)))
        if inner_w > 0:
            x0 = bar_x + 1; y0 = bar_y + 1
            x1 = x0 + inner_w - 1; y1 = bar_y + bar_h - 1
            dm.rect_safe((x0, y0, x1, y1), fill=c)

        # Спарклиния под полосой
        self._cpu_hist.append(cpu)
        hist = list(self._cpu_hist)
        if len(hist) >= 2:
            vmin = min(hist); vmax = max(hist); rng = (vmax - vmin) or 1.0
            w = min(bar_w, dm.content_width)
            h = 12
            step = (w - 1) / (len(hist) - 1)
            pts = []
            base_x = bar_x
            base_y = min(bar_y + bar_h + 4, dm.content_bottom - h)
            for i, v in enumerate(hist):
                px = base_x + int(i * step)
                py = base_y + int(h - 1 - ((v - vmin) / rng) * (h - 1))
                pts.append((px, py))
            # обрежем точки по правой/нижней кромке
            pts = [(min(dm.content_right, max(dm.content_left, x)),
                    min(dm.content_bottom, max(dm.content_top, y))) for x, y in pts]
            dm.draw.line(pts, fill=c, width=1)

        self._t = (self._t + 1) % 10000
        dm.show()
