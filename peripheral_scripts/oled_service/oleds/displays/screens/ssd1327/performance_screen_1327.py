#!/usr/bin/env python3
import math
from collections import deque
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid

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

        def gb(b):
            if not b or b <= 0: return "0"
            KB, MB, GB, TB = 1024, 1024**2, 1024**3, 1024**4
            if b >= TB: return f"{b/TB:.1f}T"
            if b >= GB: return f"{b/GB:.1f}G"
            if b >= MB: return f"{b/MB:.0f}M"
            return f"{b/KB:.0f}K"
        
        def ip_line(ip: str) -> str:
            s_full = f"IP {ip}"
            if cv.draw.textlength(s_full, font=dm.font_small) <= cv.width:
                return s_full
            try:
                a, b, c4, d = ip.split(".")
                return f"IP …{c4}.{d}"
            except Exception:
                return "IP N/A"

        def cpu_line(cpu_pct, ghz, deg):
            for s in (f"CPU {cpu_pct:.0f}% {ghz:.1f}G {deg:.0f}°",
                      f"CPU {cpu_pct:.0f}% {deg:.0f}°",
                      f"CPU {cpu_pct:.0f}%"):
                      
                if cv.draw.textlength(s, font=dm.font) <= cv.width:
                    return s
                
            return f"CPU {cpu_pct:.0f}%"

        def mem_line(mem):
            mp = float(mem.get('percent',0) or 0)
            mu, mt = gb(mem.get('used')), gb(mem.get('total'))
            variants = [
                f"Mem {mp:.0f}% {mu}/{mt}",
                f"M {mp:.0f}% {mu}/{mt}",
                f"M {mp:.0f}%",
            ]
            for s in variants:
                if cv.draw.textlength(s, font=dm.font_small) <= cv.width:
                    return s
            return variants[-1]
        
        def swp_line(swap):
            sp = float(swap.get('percent',0) or 0)
            su, st = gb(swap.get('used')), gb(swap.get('total'))
            variants = [
                f"Swp {sp:.0f}% {su}/{st}",
                f"S{sp:.0f}% {su}/{st}",
                f"S{sp:.0f}%",
            ]
            for s in variants:
                if cv.draw.textlength(s, font=dm.font_small) <= cv.width:
                    return s
            return variants[-1]

        ip    = stats.get('ip', 'N/A')
        cpu   = float(stats.get('cpu', 0) or 0.0)
        temp  = float(stats.get('temp', 0) or 0.0)
        ghz   = float(stats.get('cpu_freq', 0) or 0.0) / 1000.0
        mem   = stats.get('mem', {}) or {}
        swap  = stats.get('swap', {}) or {}

        row = 0
        row = grid.text_row(cv, dm, row, ip_line(ip), font=dm.font, fill=c)
        row = grid.text_row(cv, dm, row, cpu_line(cpu, ghz, temp), font=dm.font, fill=c)
        row = grid.text_row(cv, dm, row, mem_line(mem), font=dm.font_small, fill=c)
        row = grid.text_row(cv, dm, row, swp_line(swap), font=dm.font_small, fill=c)

        pulse = 0.95 + 0.05 * math.sin(self._t * 2 * math.pi / 30.0)
        cpu_v = max(0.0, min(1.0, (cpu/100.0) * pulse))

        row = grid.bar_row(cv, dm, row, cpu_v, height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)
        row = grid.spark_row(cv, dm, row, self._cpu_hist, height=12, gap_above=4, gap_below=0, min_rows=1, fg=c)

        self._cpu_hist.append(cpu)

        self._t = (self._t + 1) % 10000
        dm.show()
