#!/usr/bin/env python3

from .base import BaseScreen

class StorageScreen(BaseScreen):

    def draw(self, display_manager, stats):
        root_usage = stats.get('root_disk_usage', {})
        nvme_usage = stats.get('storage_disk_usage', {})
        disk_io = stats.get('disk_io', {'read': '0K', 'write': '0K'})
        docker_status = stats.get('docker_status', 'N/A')
        docker_restarts = stats.get('docker_restarts', 0)

        def format_storage(b):
            if b > 1024**4:
                return f"{b / (1024**4):.1f}T"
            return f"{b / (1024**3):.1f}G"

        ssd_used = format_storage(root_usage.get('used', 0))
        ssd_total = format_storage(root_usage.get('total', 0))
        nvme_used = format_storage(nvme_usage.get('used', 0))
        nvme_total = format_storage(nvme_usage.get('total', 0))

        display_manager.draw.text((2, 12), f"SSD: {ssd_used}/{ssd_total} {root_usage.get('percent',0):.0f}%", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 24), f"NVMe:{nvme_used}/{nvme_total} {nvme_usage.get('percent',0):.0f}%", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 36), f"Disk IO: R:{disk_io['read']} W:{disk_io['write']}", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 48), f"Docker: {docker_status} (R:{docker_restarts})", font=display_manager.font, fill=255)