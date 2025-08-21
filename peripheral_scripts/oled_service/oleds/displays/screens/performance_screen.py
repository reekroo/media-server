#!/usr/bin/env python3

from .base import BaseScreen

class PerformanceScreen(BaseScreen):

    def draw(display_manager, stats):
        ip = stats.get('ip', 'N/A')
        cpu_percent = stats.get('cpu', 0)
        cpu_temp = stats.get('temp', 0)
        cpu_freq = stats.get('cpu_freq', 0)
        
        mem = stats.get('mem', {})
        swap = stats.get('swap', {})

        def format_gb(b): return f"{b / (1024**3):.1f}"
        def format_mb(b): return f"{b / (1024**2):.0f}"

        display_manager.draw.text((2, 12), f"IP: {ip}", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 24), f"CPU:{cpu_percent:>3.0f}%/{cpu_freq/1000:.1f}G/{cpu_temp:.0f}C", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 36), f"MEM:{format_gb(mem.get('used',0))}M/{format_gb(mem.get('total',0))}G {mem.get('percent',0):>2.0f}%", font=display_manager.font, fill=255)
        display_manager.draw.text((2, 48), f"SWP:{format_gb(swap.get('used',0))}M/{format_gb(swap.get('total',0))}G {swap.get('percent',0):>2.0f}%", font=display_manager.font, fill=255)
