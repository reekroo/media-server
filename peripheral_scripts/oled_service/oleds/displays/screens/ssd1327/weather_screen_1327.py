#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G
import json

class WeatherScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    # def should_render(self, dm, stats: dict) -> bool:
    #     weather_data = stats.get("weather") or stats.get("weather_data")
    #     return weather_data is not None

    @staticmethod
    def _as_float(v, default=None):
        try:
            return float(v)
        except Exception:
            return default

    def _from_obj(self, obj):
        if obj is None:
            return {}
        get = (lambda k: getattr(obj, k)) if hasattr(obj, "__dict__") or hasattr(obj, "_asdict") else (lambda k: obj.get(k))
        try_get = lambda k: (get(k) if (hasattr(obj, k) or (isinstance(obj, dict) and k in obj)) else None)

        return {
            "location":    try_get("location_name"),
            "temp":        try_get("temperature"),
            "feels":       try_get("feels_like"),
            "pressure":    try_get("pressure"),
            "humidity":    try_get("humidity"),
            "description": try_get("description"),
            "source":      try_get("source"),
        }

    def _parse_json(self, s: str):
        try:
            return json.loads(s)
        except Exception:
            return None

    def _extract(self, stats: dict):
        container = stats.get("weather")
        if container is None:
            container = stats.get("weather_data")

        if isinstance(container, str):
            parsed = self._parse_json(container)
            if parsed is not None:
                return self._from_obj(parsed)

        if container is not None:
            return self._from_obj(container)

        flat_keys = ("location_name", "temperature", "feels_like", "pressure", "humidity", "description", "source")
        if any(k in stats for k in flat_keys):
            return self._from_obj(stats)

        return {
            "location": None, "temp": None, "feels": None,
            "pressure": None, "humidity": None, "description": None, "source": None
        }

    def _fmt_temp(self, v):
        f = self._as_float(v)
        return f"{f:.0f}°" if f is not None else "—°"

    def _fmt_feels(self, v):
        f = self._as_float(v)
        return f"Feels {f:.0f}°" if f is not None else "Feels —°"

    def _fmt_hum_press(self, hum, press, cv, dm):
        h = self._as_float(hum)
        p = self._as_float(press)
        h_txt = f"Hum {h:.0f}%" if h is not None else "Hum —"
        p_txt = f"Press {int(p)}" if p is not None else "Press —"
        full  = f"{h_txt}   {p_txt}"
        short = f"{h_txt} {p_txt}"
        return G.fit_text(cv, dm.font, [full, short])

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        w = self._extract(stats)

        if not any((w["temp"], w["feels"], w["description"], w["location"], w["pressure"], w["humidity"])):
            row = 0
            row = G.text_row(cv, dm, row, "Weather", font=dm.font_small, fill=c)
            row = G.blank_row(row, 1)
            row = G.box_row(cv, dm, row, "N/A", rows=2)
            dm.show()
            return

        row = 0
        row = G.text_row(cv, dm, row, "Weather", font=dm.font_small, fill=c)

        loc  = str(w["location"] or "—")
        desc = str(w["description"] or "").strip()
        line_full = f"{loc} — {desc}" if desc else loc

        def short_loc(name: str) -> str:
            try:
                return name.split(",")[0].strip() or name
            except Exception:
                return name

        location_line = G.fit_text(cv, dm.font_small, [line_full, loc, short_loc(loc)])
        row = G.text_row(cv, dm, row, location_line, font=dm.font_small, fill=c)

        temp_txt = self._fmt_temp(w["temp"])
        row = G.box_row(cv, dm, row, temp_txt, rows=2)

        row = G.text_row(cv, dm, row, self._fmt_feels(w["feels"]), font=dm.font, fill=c)
        row = G.text_row(cv, dm, row, self._fmt_hum_press(w["humidity"], w["pressure"], cv, dm), font=dm.font, fill=c)

        src = str(w["source"] or "").strip()
        if src:
            row = G.text_row(cv, dm, row, f"Src: {src}", font=dm.font_small, fill=c)

        dm.show()