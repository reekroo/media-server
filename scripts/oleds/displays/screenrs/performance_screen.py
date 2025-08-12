#!/usr/bin/env python3

def draw(display_manager, stats):
    ip = stats.get('ip', 'N/A')
    cpu = stats.get('cpu', 0)
    mem = stats.get('mem', 0)
    temp = stats.get('temp', 0)
    swap = stats.get('swap', 0)
    uptime = stats.get('uptime', '00:00')
    throughput = stats.get('network_throughput', {'download': '0K/s', 'upload': '0K/s'})

    display_manager.draw.text((2, 12), f"IP: {ip}", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 24), f"CPU:{cpu:>3.0f}% MEM:{mem:>3.0f}%", font=display_manager.font, fill=255)
    display_manager.draw.text((2, 36), f"TMP:{temp:>3.0f}C SWP:{swap:>3.0f}%", font=display_manager.font, fill=255)
    
    display_manager.image.paste(display_manager.icons["ARROW_DOWN"], (2, 49))
    display_manager.draw.text((14, 48), f"{throughput['download']:<6}", font=display_manager.font, fill=255)
    display_manager.image.paste(display_manager.icons["ARROW_UP"], (68, 49))
    display_manager.draw.text((80, 48), f"{throughput['upload']:<6}", font=display_manager.font, fill=255)