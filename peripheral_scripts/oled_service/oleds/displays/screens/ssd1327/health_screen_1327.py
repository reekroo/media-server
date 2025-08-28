#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas

class HealthScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        uptime = stats.get('uptime','00:00')
        temp   = float(stats.get('temp',0) or 0.0)
        nvme_t = float(stats.get('nvme_temp',0) or 0.0)
        volt   = float(stats.get('core_voltage',0) or 0.0)
        thr    = str(stats.get('throttling','N/A'))

        row = 0
        row = cv.text_row(row, f"Uptime {uptime}", font=dm.font, fill=c)
        row = cv.text_row(row, f"CPU {temp:.0f}C    NVMe {nvme_t:.0f}C", font=dm.font, fill=c)
        row = cv.text_row(row, f"Core V {volt:.2f}V", font=dm.font, fill=c)
        row = cv.text_row(row, f"Throttled: {thr}", font=dm.font, fill=c)

        # индикатор состояния справа от первой строки
        ok = (thr == "NO")
        box = "■" if not ok else "□"
        cv.text(cv.right - 12, cv.top, box, font=dm.font, fill=c)

        dm.show()
