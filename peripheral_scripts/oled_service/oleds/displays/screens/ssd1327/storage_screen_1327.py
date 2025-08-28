#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas

class StorageScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        root = stats.get('root_disk_usage', {}) or {}
        data = stats.get('storage_disk_usage', {}) or {}
        io   = stats.get('disk_io', {'read':'0K', 'write':'0K'}) or {}

        def gb(b): return f"{(b or 0)/(1024**3):.1f}G"
        def v(p):  return max(0.0, min(1.0, (root.get('percent',0)/100 if p=='root' else data.get('percent',0)/100)))

        row = 0
        row = cv.text_row(row, f"/      {root.get('percent',0):.0f}%  {gb(root.get('used'))}/{gb(root.get('total'))}", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 12, v('root'), fg=c, bg=dm.theme.background, border=c)
        row += 1

        row = cv.text_row(row, f"/mnt   {data.get('percent',0):.0f}%  {gb(data.get('used'))}/{gb(data.get('total'))}", font=dm.font, fill=c)
        cv.bar(cv.left, cv.top + row*Canvas._line_height(dm.font) - 2, min(120, cv.width), 12, v('data'), fg=c, bg=dm.theme.background, border=c)
        row += 1

        row = cv.text_row(row, f"IO  R:{io.get('read','0K')}/s  W:{io.get('write','0K')}/s", font=dm.font_small, fill=c)

        dm.show()
