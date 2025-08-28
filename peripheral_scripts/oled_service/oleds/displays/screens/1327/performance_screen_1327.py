#!/usr/bin/env python3
from ..base import BaseScreen  # интерфейс неизменен

class PerformanceScreen1327(BaseScreen):
    def draw(self, display_manager, stats):
        dm = display_manager
        c = dm.color()

        dm.begin(stats)
        dm.draw_status_bar(stats)

        ip = stats.get('ip', 'N/A')
        cpu = stats.get('cpu', 0)
        temp = stats.get('temp', 0)
        freq = stats.get('cpu_freq', 0)
        mem = stats.get('mem', {})
        swap = stats.get('swap', {})

        def gb(b): return f"{b/(1024**3):.1f}G"

        # заголовок
        dm.draw.text((4, 22), f"IP {ip}", font=dm.font_small, fill=c)
        dm.draw.text((4, 40), f"CPU {cpu:>3.0f}%  {freq/1000:.1f}GHz  {temp:.0f}C", font=dm.font, fill=c)
        dm.draw.text((4, 58), f"MEM {gb(mem.get('used',0))}/{gb(mem.get('total',0))}  {mem.get('percent',0):.0f}%", font=dm.font, fill=c)
        dm.draw.text((4, 76), f"SWP {gb(swap.get('used',0))}/{gb(swap.get('total',0))}  {swap.get('percent',0):.0f}%", font=dm.font, fill=c)

        # простая полоска загрузки CPU в полутоне
        bar_x, bar_y, bar_w, bar_h = 4, 96, 120, 12
        dm.draw.rectangle((bar_x, bar_y, bar_x+bar_w, bar_y+bar_h), outline=c, width=1)
        fill_w = int(bar_w * max(0, min(100, cpu)) / 100)
        dm.draw.rectangle((bar_x+1, bar_y+1, bar_x+fill_w-1, bar_y+bar_h-1), fill=c)

        dm.show()
