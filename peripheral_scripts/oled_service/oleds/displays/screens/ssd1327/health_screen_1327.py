#!/usr/bin/env python3
from ..base import BaseScreen

class HealthScreen1327(BaseScreen):
    def draw(self, display_manager, stats):
        dm = display_manager
        c = dm.color()
        dm.begin(stats)
        dm.draw_status_bar(stats)

        core_v = stats.get('core_voltage', 0.0)
        throt  = stats.get('throttling', 'N/A')
        uptime = stats.get('uptime', '00:00')
        nvme_t = stats.get('nvme_temp', 0)
        thr    = stats.get('network_throughput', {'download':'0K/s','upload':'0K/s'})

        dm.draw.text((4, 24), "Health", font=dm.font_large, fill=c)
        dm.draw.text((4, 50), f"Core {core_v:.2f}V   NVMe {nvme_t:.0f}C", font=dm.font, fill=c)
        dm.draw.text((4, 68), f"Throttled: {throt}", font=dm.font, fill=c)
        dm.draw.text((4, 86), f"Uptime: {uptime}", font=dm.font, fill=c)

        dm.draw.text((4, 104), f"↓ {thr['download']}   ↑ {thr['upload']}", font=dm.font, fill=c)
        dm.show()
