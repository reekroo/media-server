#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G

class WeatherScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def _as_float(self, v, default=None):
        try:
            return float(v)
        except Exception:
            return default

    def _extract(self, stats):
        w = stats.get("weather") or stats.get("weather_data") or {}
        out = {
            "location": None,
            "temp": None,
            "feels": None,
            "pressure": None,
            "humidity": None,
            "description": None,
            "source": None,
        }
        
        for key in ("location_name", "temperature", "feels_like", "pressure", "humidity", "description", "source"):
            val = None
            if hasattr(w, key):
                val = getattr(w, key)
            elif isinstance(w, dict):
                val = w.get(key)
            out_key = {
                "location_name": "location",
                "temperature": "temp",
                "feels_like": "feels",
                "pressure": "pressure",
                "humidity": "humidity",
                "description": "description",
                "source": "source",
            }[key]
            out[out_key] = val
        return out

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
        full = f"{h_txt}   {p_txt}"
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

        loc = str(w["location"] or "—")
        desc = str(w["description"] or "").strip()
        line_full = f"{loc} — {desc}" if desc else loc
        
        def short_loc(name: str) -> str:
            try:
                return name.split(",")[0].strip() or name
            except Exception:
                return name

        location_line = G.fit_text(
            cv, dm.font_small,
            [line_full, loc, short_loc(loc)]
        )
        row = G.text_row(cv, dm, row, location_line, font=dm.font_small, fill=c)

        temp_txt = self._fmt_temp(w["temp"])
        row = G.box_row(cv, dm, row, temp_txt, rows=2)

        feels_line = self._fmt_feels(w["feels"])
        row = G.text_row(cv, dm, row, feels_line, font=dm.font, fill=c)

        hp_line = self._fmt_hum_press(w["humidity"], w["pressure"], cv, dm)
        row = G.text_row(cv, dm, row, hp_line, font=dm.font, fill=c)

        src = str(w["source"] or "").strip()
        if src:
            row = G.text_row(cv, dm, row, f"Src: {src}", font=dm.font_small, fill=c)

        dm.show()