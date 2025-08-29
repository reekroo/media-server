#!/usr/bin/env python3
import os
import re
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G


class NetworkScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        # Нормировка баров: по умолчанию 10 MB/s; можно задать через ENV OLED_NET_CAP_MBPS
        cap_env = os.getenv("OLED_NET_CAP_MBPS")
        try:
            self.cap_bps = float(cap_env) * 1024 * 1024 if cap_env else 10 * 1024 * 1024.0
        except Exception:
            self.cap_bps = 10 * 1024 * 1024.0

    # -------- helpers --------
    def _ip_line(self, cv, dm, ip: str) -> str:
        """Строка IP с сокращением, если не влезает."""
        full = f"IP {ip}"
        if cv.draw.textlength(full, font=dm.font_small) <= cv.width:
            return full
        try:
            parts = ip.split(".")
            return f"IP …{parts[-2]}.{parts[-1]}"
        except Exception:
            return "IP N/A"

    def _rate_parse(self, s: str) -> float:
        """ '320K/s' | '2.4M/s' | '500K' -> bytes/s """
        if not s:
            return 0.0
        s = s.strip().lower().replace("/s", "")
        m = re.match(r"^([0-9]+(?:\.[0-9]+)?)([km]?)$", s)
        if not m:
            return 0.0
        val = float(m.group(1))
        unit = m.group(2)
        if unit == "m":
            val *= 1024 * 1024
        elif unit == "k":
            val *= 1024
        return val

    def _fmt_status(self, name: str, val) -> str:
        if val is True:
            st = "ON"
        elif val is False:
            st = "OFF"
        else:
            st = "N/A"
        return f"{name} {st}"

    # -------- draw --------
    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        ip = stats.get("ip", "N/A")
        thr = stats.get("network_throughput") or {}
        up_txt = (thr.get("upload") or "0K/s")
        dn_txt = (thr.get("download") or "0K/s")

        # статусы
        wifi_conn = stats.get("status_wifi_connected", None)  # только connected
        lan_conn  = stats.get("status_lan", None)
        bt_en     = stats.get("status_bluetooth", None)

        row = 0
        # IP строка
        row = G.text_row(cv, dm, row, self._ip_line(cv, dm, ip), font=dm.font_small, fill=c)

        # Каждому статусу — своя строка (small)
        row = G.text_row(cv, dm, row, self._fmt_status("WiFi", wifi_conn), font=dm.font_small, fill=c)
        row = G.text_row(cv, dm, row, self._fmt_status("LAN",  lan_conn),  font=dm.font_small, fill=c)
        row = G.text_row(cv, dm, row, self._fmt_status("BT",   bt_en),     font=dm.font_small, fill=c)

        # Трафик: одна строка или две — по месту
        both = f"↑{up_txt}  ↓{dn_txt}"
        if cv.draw.textlength(both, font=dm.font) <= cv.width:
            row = G.text_row(cv, dm, row, both, font=dm.font, fill=c)

            up_v = max(0.0, min(1.0, self._rate_parse(up_txt) / self.cap_bps))
            dn_v = max(0.0, min(1.0, self._rate_parse(dn_txt) / self.cap_bps))

            row = G.bar_row(cv, dm, row, up_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                            fg=c, bg=dm.theme.background, border=c)
            row = G.bar_row(cv, dm, row, dn_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                            fg=c, bg=dm.theme.background, border=c)
        else:
            # Разносим на две строки с барами под каждой
            row = G.text_row(cv, dm, row, f"↑{up_txt}", font=dm.font, fill=c)
            up_v = max(0.0, min(1.0, self._rate_parse(up_txt) / self.cap_bps))
            row = G.bar_row(cv, dm, row, up_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                            fg=c, bg=dm.theme.background, border=c)

            row = G.text_row(cv, dm, row, f"↓{dn_txt}", font=dm.font, fill=c)
            dn_v = max(0.0, min(1.0, self._rate_parse(dn_txt) / self.cap_bps))
            row = G.bar_row(cv, dm, row, dn_v, height=10, gap_above=2, gap_below=2, min_rows=1,
                            fg=c, bg=dm.theme.background, border=c)

        dm.show()
