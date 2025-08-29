#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
from ...ui import format as F

class StorageScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c=dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv=Canvas.from_display(dm)

        root = stats.get('root_disk_usage') or {}
        data = stats.get('storage_disk_usage') or {}
        io   = stats.get('disk_io') or {}

        def line_fs(label, d, font):
            p=float(d.get('percent',0) or 0); u,t=F.fmt_bytes(d.get('used')),F.fmt_bytes(d.get('total'))
            return G.fit_text(cv, font, [f"{label} {p:.0f}% {u}/{t}", f"{label} {p:.0f}%"])

        row=0
        row = G.text_row(cv, dm, row, line_fs("SSD", root, dm.font), font=dm.font, fill=c)
        row = G.bar_row(cv, dm, row, (float(root.get('percent',0) or 0)/100.0),
                        height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)

        row = G.text_row(cv, dm, row, line_fs("NWMe", data, dm.font), font=dm.font, fill=c)
        row = G.bar_row(cv, dm, row, (float(data.get('percent',0) or 0)/100.0),
                        height=12, gap_above=2, gap_below=2, min_rows=1, fg=c, bg=dm.theme.background, border=c)

        io_full  = f"IO R:{(io.get('read') or '0K')}/s  W:{(io.get('write') or '0K')}/s"
        io_short = f"R:{(io.get('read') or '0K')}  W:{(io.get('write') or '0K')}"
        io_line  = G.fit_text(cv, dm.font_small, [io_full, io_short])
        row = G.text_row(cv, dm, row, io_line, font=dm.font_small, fill=c)

        dm.show()
