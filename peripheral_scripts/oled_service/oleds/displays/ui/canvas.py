#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PIL import ImageDraw, ImageFont

@dataclass
class Canvas:
    draw: ImageDraw.ImageDraw
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int
    color: Tuple[int, ...]  # default color

    @classmethod
    def from_display(cls, dm) -> "Canvas":
        return cls(
            draw=dm.draw,
            left=dm.content_left,
            top=dm.content_top,
            right=dm.content_right,
            bottom=dm.content_bottom,
            width=dm.content_width,
            height=dm.content_height,
            color=dm.color(),
        )

    @staticmethod
    def _line_height(font: ImageFont.ImageFont, extra: int = 2) -> int:
        try:
            bbox = font.getbbox("Ag")
            h = bbox[3] - bbox[1]
        except Exception:
            h = getattr(font, "size", 12)
        return int(h + extra)

    def _clamp_rect(self, x0, y0, x1, y1) -> Optional[Tuple[int,int,int,int]]:
        X0 = max(self.left,  min(self.right,  int(x0)))
        Y0 = max(self.top,   min(self.bottom, int(y0)))
        X1 = max(self.left,  min(self.right,  int(x1)))
        Y1 = max(self.top,   min(self.bottom, int(y1)))
        if X1 < X0 or Y1 < Y0:
            return None
        return (X0, Y0, X1, Y1)

    def _ellipsis(self, text: str, max_w: int, font) -> str:
        if self.draw.textlength(text, font=font) <= max_w:
            return text
        ell, w_ell = "…", self.draw.textlength("…", font=font)
        if w_ell > max_w:
            return ""
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.draw.textlength(text[:mid], font=font) + w_ell <= max_w:
                lo = mid + 1
            else:
                hi = mid
        return text[:max(0, lo-1)] + ell

    # --- text ---
    def text(self, x: int, y: int, s: str, *, font, fill=None, max_w: Optional[int]=None):
        fill = self.color if fill is None else fill
        if max_w is not None:
            s = self._ellipsis(s, max_w, font)
        self.draw.text((x, y), s, font=font, fill=fill)

    def text_row(self, row_idx: int, s: str, *, font, fill=None, pad_left: int=0) -> int:
        lh = self._line_height(font)
        y = self.top + row_idx * lh
        if y > self.bottom:
            return row_idx + 1
        self.text(self.left + pad_left, y, s, font=font, fill=fill, max_w=self.width - pad_left)
        return row_idx + 1

    # --- rect/bar/sparkline ---
    def rect(self, x0, y0, x1, y1, *, outline=None, fill=None, width=1):
        r = self._clamp_rect(x0, y0, x1, y1)
        if not r:
            return
        if fill is not None:
            self.draw.rectangle(r, fill=fill)
        if outline is not None:
            self.draw.rectangle(r, outline=outline, width=width)

    def bar(self, x, y, w, h, value01: float, *, fg=None, bg=None, border=None):
        fg = self.color if fg is None else fg
        v = max(0.0, min(1.0, value01))
        if bg is not None:
            self.rect(x, y, x+w, y+h, fill=bg)
        if border is not None:
            self.rect(x, y, x+w, y+h, outline=border)
        inner_w = max(0, int(round((w-2) * v)))
        if inner_w > 0:
            self.rect(x+1, y+1, x+1+inner_w-1, y+h-1, fill=fg)

    def sparkline(self, x, y, w, h, values: List[float], *, fg=None):
        if not values:
            return
        fg = self.color if fg is None else fg
        n = len(values)
        if n == 1:
            self.draw.line((x, y+h//2, x+w, y+h//2), fill=fg)
            return
        vmin = min(values); vmax = max(values); rng = (vmax - vmin) or 1.0
        step = (w - 1) / (n - 1)
        pts = []
        for i, v in enumerate(values):
            px = x + int(i * step)
            py = y + int(h - 1 - ((v - vmin) / rng) * (h - 1))
            px = min(self.right, max(self.left, px))
            py = min(self.bottom, max(self.top, py))
            pts.append((px, py))
        self.draw.line(pts, fill=fg, width=1)
