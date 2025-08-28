#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas

class SystemScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip   = stats.get('ip','N/A')
        up   = stats.get('uptime','00:00')
        cpu  = float(stats.get('cpu',0) or 0.0)
        freq = float(stats.get('cpu_freq',0) or 0.0)

        row = 0
        row = cv.text_row(row, f"Uptime {up}", font=dm.font, fill=c)
        row = cv.text_row(row, f"CPU {cpu:.0f}%   {freq/1000:.1f}GHz", font=dm.font, fill=c)
        row = cv.text_row(row, f"IP {ip}", font=dm.font, fill=c)

        dm.show()
