#!/usr/bin/env python3
from typing import Optional
from ..base import BaseScreen
from ...ui.canvas import Canvas
from oleds.providers.weather_provider import WeatherProvider, WeatherData

class WeatherScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def __init__(self):
        self.provider = WeatherProvider()
        self._last: Optional[WeatherData] = None

    def should_render(self, dm, stats) -> bool:
        data = self.provider.get_weather(timeout=0.05)
        if data:
            self._last = data
            return True
        return self._last is not None

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        data = self.provider.get_weather(timeout=0.2)
        if data:
            self._last = data

        if not self._last:
            cv.text(cv.left, cv.top + 24, "Weather: no data", font=dm.font, fill=c)
            dm.show()
            return

        w = self._last
        row = 0
        row = cv.text_row(row, f"{w.location_name}", font=dm.font, fill=c)
        row = cv.text_row(row, f"{int(round(w.temperature))}°   feels {int(round(w.feels_like))}°", font=dm.font_large, fill=c)
        row = cv.text_row(row, f"{(w.description or '').capitalize()}", font=dm.font, fill=c)
        row = cv.text_row(row, f"H {w.humidity}%    {w.pressure} hPa", font=dm.font, fill=c)
        src = f"[{w.source}]"
        tw = cv.draw.textlength(src, font=dm.font_small)
        cv.text(cv.right - tw, cv.top + row*Canvas._line_height(dm.font_small), src, font=dm.font_small, fill=c)

        dm.show()
