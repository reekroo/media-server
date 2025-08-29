#!/usr/bin/env python3
import math
from collections import deque
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
from ...ui import format as F

class PerformanceScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self._t=0
        self._cpu_hist=deque(maxlen=60)

    def draw(self, dm, stats):
        c=dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv=Canvas.from_display(dm)

        ip   = stats.get('ip','N/A')
        cpu  = float(stats.get('cpu',0) or 0.0)
        temp = float(stats.get('temp',0) or 0.0)
        ghz  = float(stats.get('cpu_freq',0) or 0.0)/1000.0
        mem  = stats.get('mem',{}) or {}
        swap = stats.get('swap',{}) or {}

        ip_line = G.fit_text(cv, dm.font_small, [f"IP {ip}", F.short_ip(ip)])
        cpu_line = G.fit_text(cv, dm.font, [
            f"CPU {cpu:.0f}% {ghz:.1f}G {temp:.0f}°",
            f"CPU {cpu:.0f}% {temp:.0f}°",
            f"CPU {cpu:.0f}%",
        ])
        m_p = float(mem.get('percent',0) or 0); mu, mt = F.fmt_bytes(mem.get('used')), F.fmt_bytes(mem.get('total'))
        s_p = float(swap.get('percent',0) or 0); su, st = F.fmt_bytes(swap.get('used')),F.fmt_bytes(swap.get('total'))
        mem_line = G.fit_text(cv, dm.font_small, [
            f"Mem {m_p:.0f}% {mu}/{mt}",
            f"M{m_p:.0f}% {mu}/{mt}",
            f"M{m_p:.0f}%%",
        ])
        swp_line = G.fit_text(cv, dm.font_small, [
            f"Swp {s_p:.0f}% {su}/{st}",
            f"S{s_p:.0f}% {su}/{st}",
            f"S{s_p:.0f}%",
        ])

        row=0
        row=G.text_row(cv,dm,row,ip_line,font=dm.font_small,fill=c)
        row=G.text_row(cv,dm,row,cpu_line,font=dm.font_small,fill=c)
        row=G.text_row(cv,dm,row,mem_line,font=dm.font_small,fill=c)
        row=G.text_row(cv,dm,row,swp_line,font=dm.font_small,fill=c)

        pulse = 0.95 + 0.05*math.sin(self._t*2*math.pi/30.0)
        cpu_v = max(0.0, min(1.0, (cpu/100.0)*pulse))
        row = G.bar_row(cv, dm, row, cpu_v, height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)

        self._cpu_hist.append(cpu)
        row = G.spark_row(cv, dm, row, list(self._cpu_hist), height=12, gap_above=4, gap_below=0, min_rows=1, fg=c)

        self._t=(self._t+1)%10000
        dm.show()
