#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G

class SystemScreen1327(BaseScreen):
    """
    System (SSD1327):
      • System (title)
      • Up 02:13  (или 2d 03:10)
      • CPU 37% 1.4G  (если не влезает -> CPU 37%)
      • Mem 36% 0.7/1.9G  (если не влезает -> Mem 36%)
      • / 22% 13/60G     (если не влезает -> / 22%)
      • IP 10.0.0.42     (если не влезает -> IP …0.42)
      • Docker RUN/STOP  (если нет данных -> Docker N/A)
    """
    HANDLES_BACKGROUND = True

    # ---- helpers ----
    @staticmethod
    def _gb(b):
        if not b or b <= 0: return "0"
        KB, MB, GB, TB = 1024, 1024**2, 1024**3, 1024**4
        if b >= TB: return f"{b/TB:.1f}T"
        if b >= GB: return f"{b/GB:.1f}G"
        if b >= MB: return f"{b/MB:.0f}M"
        return f"{b/KB:.0f}K"

    @staticmethod
    def _ip_short(ip: str) -> str:
        try:
            parts = str(ip).split(".")
            if len(parts) == 4:
                return f"IP …{parts[-2]}.{parts[-1]}"
        except Exception:
            pass
        return "IP N/A"

    def _cpu_line(self, cv, dm, cpu_pct: float, ghz: float) -> str:
        variants = [
            f"CPU {cpu_pct:.0f}% {ghz:.1f}G",
            f"CPU {cpu_pct:.0f}%",
        ]
        for s in variants:
            if cv.draw.textlength(s, font=dm.font) <= cv.width:
                return s
        return variants[-1]

    def _mem_line(self, cv, dm, mem: dict) -> str:
        p = float(mem.get('percent', 0) or 0)
        used, total = self._gb(mem.get('used')), self._gb(mem.get('total'))
        A = f"Mem {p:.0f}% {used}/{total}"
        B = f"Mem {p:.0f}%"
        return A if cv.draw.textlength(A, font=dm.font_small) <= cv.width else B

    def _root_line(self, cv, dm, root: dict) -> str:
        p = float(root.get('percent', 0) or 0)
        used, total = self._gb(root.get('used')), self._gb(root.get('total'))
        A = f"/ {p:.0f}% {used}/{total}"
        B = f"/ {p:.0f}%"
        return A if cv.draw.textlength(A, font=dm.font_small) <= cv.width else B

    def _docker_line(self, stats) -> str:
        # краткий статус контейнера
        raw = (stats.get("docker_status") or "").strip().lower()
        is_run = bool(stats.get("status_docker", False))
        if is_run:
            label = "RUN"
        elif raw in ("restarting", "restart"):
            label = "RESTART"
        elif raw in ("exited", "stopped", "dead"):
            label = "STOP"
        else:
            label = raw.upper() if raw else "N/A"
        return f"Docker {label}"

    # ---- draw ----
    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        # данные
        uptime = stats.get('uptime', '00:00')
        cpu    = float(stats.get('cpu', 0) or 0.0)
        ghz    = float(stats.get('cpu_freq', 0) or 0.0) / 1000.0
        mem    = stats.get('mem', {}) or {}
        root   = stats.get('root_disk_usage', {}) or {}
        ip     = stats.get('ip', 'N/A')

        row = 0
        # Title
        row = G.text_row(cv, dm, row, "System", font=dm.font_small, fill=c)
        # Uptime
        row = G.text_row(cv, dm, row, f"Up {uptime}", font=dm.font, fill=c)
        # CPU
        row = G.text_row(cv, dm, row, self._cpu_line(cv, dm, cpu, ghz), font=dm.font, fill=c)
        # Mem (small)
        row = G.text_row(cv, dm, row, self._mem_line(cv, dm, mem), font=dm.font_small, fill=c)
        # Root disk (small)
        row = G.text_row(cv, dm, row, self._root_line(cv, dm, root), font=dm.font_small, fill=c)
        # IP (small)
        ip_line_full = f"IP {ip}"
        ip_line = ip_line_full if cv.draw.textlength(ip_line_full, font=dm.font_small) <= cv.width else self._ip_short(ip)
        row = G.text_row(cv, dm, row, ip_line, font=dm.font_small, fill=c)
        # Docker (small)
        row = G.text_row(cv, dm, row, self._docker_line(stats), font=dm.font_small, fill=c)

        dm.show()
