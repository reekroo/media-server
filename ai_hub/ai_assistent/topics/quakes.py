import json
import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.simple_text_formatter import SimpleTextFormatter

_SYS_HINT = (
    "You are a seismology assistant. Earthquake prediction is not reliable — do NOT claim forecasts. "
    "Assess recent activity only: magnitude distribution, clusters, qualitative aftershock likelihood, "
    "and an attention level with rationale."
)

class QuakesAssessment(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return SimpleTextFormatter()

    def build_prompt(self, payload: dict) -> str:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        return textwrap.dedent(f"""
            {_SYS_HINT}

            OUTPUT STYLE (STRICT):
            - Simple Markdown only (no HTML, no code fences).
            - Use short paragraphs and compact bullets (<= ~120 chars per line).
            - Use these sections with emojis and bold titles:

            📈 *Trend overview*
            - 2–4 short bullets on magnitude & frequency changes (dates if relevant).

            🗺️ *Spatial clusters*
            - 1–2 bullets naming approximate areas (coords or nearby towns) and what changed.

            🌊 *Aftershock probability*
            - One line: Low / Medium / High (brief why). Avoid numeric probabilities.

            ⚠️ *Attention level*
            - One line with badge: 🟢 Low / 🟡 Medium / 🔴 High — plus a 1-line rationale.

            DATA (JSON, keys may include events with ts/mag/lat/lon/depth):
            {payload_json}
        """).strip()