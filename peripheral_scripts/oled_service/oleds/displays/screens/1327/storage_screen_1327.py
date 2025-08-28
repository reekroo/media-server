#!/usr/bin/env python3
from ..base import BaseScreen

class StorageScreen1327(BaseScreen):
    def draw(self, display_manager, stats):
        dm = display_manager
        c = dm.color()
        dm.begin(stats)
        dm.draw_status_bar(stats)

        root = stats.get('root_disk_usage', {})
        nvme = stats.get('storage_disk_usage', {})
        io = stats.get('disk_io', {'read':'0K','write':'0K'})
        docker_status = stats.get('docker_status', 'N/A')
        docker_restarts = stats.get('docker_restarts', 0)

        def fmt(b):
            if b > 1024**4: return f"{b/(1024**4):.1f}T"
            return f"{b/(1024**3):.1f}G"

        dm.draw.text((4, 24), "Storage", font=dm.font_large, fill=c)

        dm.draw.text((4, 50),  f"SSD  {fmt(root.get('used',0))}/{fmt(root.get('total',0))}  {root.get('percent',0):.0f}%", font=dm.font, fill=c)
        dm.draw.text((4, 68),  f"NVMe {fmt(nvme.get('used',0))}/{fmt(nvme.get('total',0))}  {nvme.get('percent',0):.0f}%", font=dm.font, fill=c)
        dm.draw.text((4, 86),  f"IO   R:{io['read']}  W:{io['write']}", font=dm.font, fill=c)
        dm.draw.text((4, 104), f"Docker {docker_status} (R:{docker_restarts})", font=dm.font, fill=c)

        dm.show()
