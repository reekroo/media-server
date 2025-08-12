#!/usr/bin/env python3

def draw(display_manager, stats):
    root_usage = stats.get('root_disk_usage', 0)
    nvme_usage = stats.get('storage_disk_usage', 0)
    disk_io = stats.get('disk_io', {'read': '0K', 'write': '0K'})
    docker_status = stats.get('docker_status', 'N/A')
    docker_restarts = stats.get('docker_restarts', 0)

    display_manager.draw.text((2, 12), f"SSD:  {root_usage}%", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 24), f"NVMe: {nvme_usage}%", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 36), f"Disk IO: R:{disk_io['read']} W:{disk_io['write']}", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 48), f"Docker: {docker_status} (R:{docker_restarts})", font=display_manager.font, fill=255)