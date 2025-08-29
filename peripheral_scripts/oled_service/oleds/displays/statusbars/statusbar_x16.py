#!/usr/bin/env python3
from typing import Dict

from .base import StatusBarBase

class StatusBarGray16(StatusBarBase):
    def draw(self, dm, statuses: Dict):
        padding = 2
        gap = 2
        x = padding
        y = padding
        items = [
            ("DOCKER_OK" if statuses.get("status_docker") else "DOCKER_FAIL"),
            ("STORAGE_OK" if statuses.get("status_root_disk") else "STORAGE_FAIL"),
            ("NVME_OK" if statuses.get("status_storage_disk") else "NVME_FAIL"),
            ("WIFI_OK" if statuses.get("status_wifi") else "WIFI_FAIL"),
            ("VOLTAGE_OK" if statuses.get("status_voltage") else "VOLTAGE_FAIL"),
        ]
        for name in items:
            ic = dm._get_icon(name)
            if ic:
                dm.image.paste(ic, (x, y))
                x += self.icon_size + gap

        ip = dm._last_stats.get("ip", "")
        if ip:
            c = self.color()
            tw = dm.draw.textlength(ip, font=dm.font_small)
            dm.draw.text((dm.width - tw - padding, y), ip, font=dm.font_small, fill=c)