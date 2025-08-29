#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
from ...ui import format as F

class SystemScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def draw(self, dm, stats):
        c=dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv=Canvas.from_display(dm)

        uptime = stats.get('uptime','00:00')
        cpu    = float(stats.get('cpu',0) or 0.0)
        ghz    = float(stats.get('cpu_freq',0) or 0.0)/1000.0
        mem    = stats.get('mem',{}) or {}
        root   = stats.get('root_disk_usage',{}) or {}
        ip     = stats.get('ip','N/A')
        docker = (stats.get("docker_status") or "").strip().lower()
        is_run = bool(stats.get("status_docker", False))
        dock_label = "RUN" if is_run else ("RESTART" if docker in ("restarting","restart") else "STOP" if docker in ("exited","stopped","dead") else docker.upper() if docker else "N/A")

        cpu_line = G.fit_text(cv, dm.font, [
            f"CPU {cpu:.0f}% {ghz:.1f}G",
            f"CPU {cpu:.0f}%"
        ])

        mp = float(mem.get('percent',0) or 0); mu, mt = F.fmt_bytes(mem.get('used')), F.fmt_bytes(mem.get('total'))
        mem_line = G.fit_text(cv, dm.font_small, [
            f"Mem {mp:.0f}% {mu}/{mt}",
            f"Mem {mp:.0f}%"
        ])

        rp = float(root.get('percent',0) or 0); ru, rt = F.fmt_bytes(root.get('used')), F.fmt_bytes(root.get('total'))
        root_line = G.fit_text(cv, dm.font_small, [
            f"/ {rp:.0f}% {ru}/{rt}",
            f"/ {rp:.0f}%"
        ])

        ip_line = G.fit_text(cv, dm.font_small, [f"IP {ip}", F.short_ip(ip)])

        row=0
        row=G.text_row(cv, dm, row, "System", font=dm.font_small, fill=c)
        row=G.text_row(cv, dm, row, f"Up {uptime}", font=dm.font, fill=c)
        row=G.text_row(cv, dm, row, cpu_line, font=dm.font, fill=c)
        row=G.text_row(cv, dm, row, mem_line, font=dm.font_small, fill=c)
        row=G.text_row(cv, dm, row, root_line, font=dm.font_small, fill=c)
        row=G.text_row(cv, dm, row, ip_line, font=dm.font_small, fill=c)
        row=G.text_row(cv, dm, row, f"Docker {dock_label}", font=dm.font_small, fill=c)
        dm.show()
