#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid

class StorageScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        root = stats.get('root_disk_usage') or {}
        data = stats.get('storage_disk_usage') or {}
        io   = stats.get('disk_io') or {}

        def gb(b):
            if not b or b <= 0: return "0"
            KB, MB, GB, TB = 1024, 1024**2, 1024**3, 1024**4
            if b >= TB: return f"{b/TB:.1f}T"
            if b >= GB: return f"{b/GB:.1f}G"
            if b >= MB: return f"{b/MB:.0f}M"
            return f"{b/KB:.0f}K"

        def line_fs(label, d):
            p = float(d.get('percent', 0) or 0)
            u, t = gb(d.get('used')), gb(d.get('total'))
            full  = f"{label} {p:.0f}% {u}/{t}"
            short = f"{label} {p:.0f}%"
            return full if cv.draw.textlength(full, font=dm.font_small) <= cv.width else short

        row = 0

        row = grid.text_row(cv, dm, row, line_fs("SSD", root), font=dm.font_small, fill=c)
        row = grid.bar_row(cv, dm, row, 
                           (float(root.get('percent', 0) or 0) / 100.0),
                           height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)

        row = grid.text_row(cv, dm, row, line_fs("NWMe", data), font=dm.font_small, fill=c)
        row = grid.bar_row(cv, dm, row, 
                           (float(data.get('percent', 0) or 0) / 100.0),
                           height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)

        io_full  = f"IO R:{(io.get('read') or '0K')}/s W:{(io.get('write') or '0K')}/s"
        io_short = f"R:{(io.get('read') or '0K')} W:{(io.get('write') or '0K')}"
        io_line  = io_full if cv.draw.textlength(io_full, font=dm.font_small) <= cv.width else io_short
        row = grid.text_row(cv, dm, row, io_line, font=dm.font_small, fill=c)

        dm.show()
