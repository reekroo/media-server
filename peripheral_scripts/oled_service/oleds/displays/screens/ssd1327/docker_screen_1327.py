#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas

class DockerScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        status = str(stats.get('docker_status', 'N/A'))
        restarts = int(stats.get('docker_restarts', stats.get('docker_restarts', 0)) or stats.get('docker_restarts', 0))
        is_run = bool(stats.get('status_docker', False))
        exit_code = stats.get('docker_exit_code', stats.get('exit_code', None))

        row = 0
        row = cv.text_row(row, "Docker", font=dm.font_small, fill=c)
        row = cv.text_row(row, f"Status: {status}", font=dm.font, fill=c)
        row = cv.text_row(row, f"Restarts: {restarts}", font=dm.font, fill=c)
        
        if exit_code is not None and exit_code != -1:
            row = cv.text_row(row, f"Exit: {exit_code}", font=dm.font, fill=c)

        badge = " RUNNING " if is_run else " STOPPED "

        bx = cv.left
        by = min(cv.bottom - 18, cv.top + row * Canvas._line_height(dm.font))
        bw, bh = min(72, cv.width), 16
        cv.rect(bx, by, bx+bw, by+bh, fill=dm.theme.background, outline=c)
        
        tw = cv.draw.textlength(badge, font=dm.font)
        tx = bx + max(0, (bw - tw)//2)
        ty = by + max(0, (bh - Canvas._line_height(dm.font))//2)
        cv.text(tx, ty, badge, font=dm.font, fill=c)

        dm.show()
