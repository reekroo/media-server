#!/usr/bin/env python3
import os
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
from ...ui import format as F
from ...ui.trend import Trend

class DiskIOScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        alpha = float(os.getenv("OLED_IO_EMA_ALPHA", "0.3"))
        decay = float(os.getenv("OLED_IO_TREND_DECAY", "0.90"))
        self.trend = Trend(n_series=2, history=120, alpha=alpha, decay=decay)

    def _grey(self, dm, level=160):
        mode = getattr(dm.image, "mode", "L") if getattr(dm, "image", None) is not None else "L"
        level = int(max(0, min(255, level)))
        if mode == "L":  return level
        if mode == "1":  return 1
        return (level, level, level)

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        dio = stats.get("disk_io") or {}
        r_bps = F.parse_rate_bps(dio.get("read"))
        w_bps = F.parse_rate_bps(dio.get("write"))

        row = 0
        row = G.text_row(cv, dm, row, "Disk I/O", font=dm.font, fill=c)
        line = G.fit_text(cv, dm.font, [
            f"R {F.fmt_bps(r_bps)}   W {F.fmt_bps(w_bps)}",
            f"R {F.fmt_bps(r_bps)} W {F.fmt_bps(w_bps)}",
            f"R {F.fmt_bps(r_bps)}"
        ])
        row = G.text_row(cv, dm, row, line, font=dm.font_small, fill=c)

        r_norm, w_norm = self.trend.update([r_bps, w_bps])
        row = G.spark_area(
            cv, dm, row,
            series_list=[r_norm, w_norm],
            colors=[self._grey(dm, 160), c],
            height=max(12, G.base_lh(dm) * 2 - 4),
            gap_above=2, gap_below=0, min_rows=2
        )

        dm.show()