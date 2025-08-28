#!/usr/bin/env python3

from ..base import BaseScreen

class HealthScreen(BaseScreen):

    def draw(self, display_manager, stats):
        core_v = stats.get('core_voltage', 0.0)
        throttling = stats.get('throttling', 'N/A')
        uptime = stats.get('uptime', '00:00')
        nvme_t = stats.get('nvme_temp', 0)
        throughput = stats.get('network_throughput', {'download': '0K/s', 'upload': '0K/s'})

        display_manager.draw.text((2, 12), f"Core:{core_v:.2f}V / NVMe:{nvme_t:.0f}C", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 24), f"Throttled: {throttling}", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 36), f"Uptime: {uptime}", font=display_manager.font, fill=255)
        
        net_down = throughput['download']
        net_up = throughput['upload']
        
        display_manager.image.paste(display_manager.icons["ARROW_DOWN"], (2, 49))
        display_manager.draw.text((14, 48), f"{net_down:<6}", font=display_manager.font, fill=255)
        display_manager.image.paste(display_manager.icons["ARROW_UP"], (68, 49))
        display_manager.draw.text((80, 48), f"{net_up:<6}", font=display_manager.font, fill=255)