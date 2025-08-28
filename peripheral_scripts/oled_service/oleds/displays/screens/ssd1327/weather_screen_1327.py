#!/usr/bin/env python3
from typing import Optional
from ..base import BaseScreen
from oleds.providers.weather_provider import WeatherProvider, WeatherData

class WeatherScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True  # экран сам чистит фон и рисует статус-бар

    def __init__(self):
        self.provider = WeatherProvider()
        self._last: Optional[WeatherData] = None

    # новый контракт: если False — фабрика может оставить страницу в списке,
    # но контроллер будет её пропускать в ротации
    def should_render(self, dm, stats) -> bool:
        # быстрый «peek»: если данные есть — сразу True
        data = self.provider.get_weather(timeout=0.05)
        if data:
            self._last = data
            return True
        # если ранее были данные — можно продолжать показывать (ещё пару кадров),
        # чтобы не мигало — по желанию можно убрать
        return self._last is not None

    def draw(self, dm, stats):
        c = dm.color()

        # так как HANDLES_BACKGROUND=True — контроллер фон не трогал
        dm.clear()
        dm.draw_status_bar(stats)

        # обновим данные «по-взрослому» (с чуть большим таймаутом)
        data = self.provider.get_weather(timeout=0.2)
        if data:
            self._last = data

        if not self._last:
            txt = "Weather: no data"
            tw = dm.draw.textlength(txt, font=getattr(dm, "font_small", dm.font))
            dm.draw.text(((dm.width - tw)//2, 60), txt, font=getattr(dm, "font_small", dm.font), fill=c)
            dm.show()
            return

        w = self._last
        font_small = getattr(dm, "font_small", dm.font)
        font_reg   = dm.font
        font_large = getattr(dm, "font_large", dm.font)

        dm.draw.text((4, 22), f"{w.location_name}", font=font_reg, fill=c)

        t = f"{int(round(w.temperature))}°"
        dm.draw.text((4, 46), t, font=font_large, fill=c)

        feels = f"feels {int(round(w.feels_like))}°"
        tx = 4 + max(48, dm.draw.textlength(t, font=font_large)) + 6
        dm.draw.text((tx, 56), feels, font=font_small, fill=c)

        desc = (w.description or "").capitalize()
        tw = dm.draw.textlength(desc, font=font_reg)
        dm.draw.text(((dm.width - tw)//2, 78), desc, font=font_reg, fill=c)

        dm.draw.text((4, 100), f"H {w.humidity}%   {w.pressure} hPa", font=font_reg, fill=c)
        src = f"[{w.source}]"
        tw = dm.draw.textlength(src, font=font_small)
        dm.draw.text((dm.width - tw - 4, 102), src, font=font_small, fill=c)

        dm.show()
