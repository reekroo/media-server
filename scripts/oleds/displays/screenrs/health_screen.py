#!/usr/bin/env python3

def draw(display_manager, stats):
    core_v = stats.get('core_voltage', 0.0)
    psu_v = stats.get('psu_voltage', 0.0)
    throttling = stats.get('throttling', 'N/A')
    uptime = stats.get('uptime', '00:00')
    nvme_t = stats.get('nvme_temp', 0)
    nvme_ps_set = stats.get('nvme_ps_set', '?')
    nvme_ps_now = stats.get('nvme_ps_now', '?')

    display_manager.draw.text((2, 12), f"C:{core_v:.2f}V   P:{psu_v:.2f}V", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 24), f"Throttled: {throttling}", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 36), f"NVMe:{nvme_t}C Up:{uptime}", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 48), f"NVMe PS: Set:{nvme_ps_set} Now:{nvme_ps_now}", font=display_manager.font, fill=255)
