#!/usr/bin/env python3

def draw(display_manager, stats):
    core_v = stats.get('core_voltage', 0.0)
    throttling = stats.get('throttling', 'N/A')
    uptime = stats.get('uptime', '00:00')
    nvme_t = stats.get('nvme_temp', 0)

    display_manager.draw.text((2, 12), f"Core:{core_v:.2f}V", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 24), f"Throttled: {throttling}", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 36), f"NVMe Temp: {nvme_t}C", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 48), f"Uptime: {uptime}", font=display_manager.font, fill=255)