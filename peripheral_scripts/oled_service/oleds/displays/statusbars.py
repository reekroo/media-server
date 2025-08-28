#!/usr/bin/env python3
from typing import Dict, Tuple

WHITE_1BIT = 255
WHITE_RGB: Tuple[int, int, int] = (255, 255, 255)

class _StatusBarBase:
    def __init__(self, icon_size: int, image_mode: str):
        self.icon_size = icon_size
        self.image_mode = image_mode

    def color(self):
        return WHITE_RGB if self.image_mode != "1" else WHITE_1BIT

    def draw(self, dm, statuses: Dict):
        raise NotImplementedError


class StatusBarMono8(_StatusBarBase):
    """ Узкий статус-бар (128×64), 5 иконок 8×8 """
    def draw(self, dm, statuses: Dict):
        icons = [
            "DOCKER_OK" if statuses.get("status_docker") else "DOCKER_FAIL",
            "STORAGE_OK" if statuses.get("status_root_disk") else "STORAGE_FAIL",
            "NVME_OK" if statuses.get("status_storage_disk") else "NVME_FAIL",
            "WIFI_OK" if statuses.get("status_wifi") else "WIFI_FAIL",
            "VOLTAGE_OK" if statuses.get("status_voltage") else "VOLTAGE_FAIL",
        ]
        positions = [0, 30, 60, 90, 120]
        for i, name in enumerate(icons):
            icon = dm._get_icon(name)
            if icon:
                dm.image.paste(icon, (positions[i], 0))


class StatusBarGray16(_StatusBarBase):
    """ Широкий статус-бар (128×128), 5 иконок 16×16 + IP справа """
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
