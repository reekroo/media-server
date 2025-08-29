from __future__ import annotations
from typing import Dict
from PIL import Image, ImageDraw, ImageFont
from oleds.configs.oled_profiles import OledProfile
from oleds.configs.themes import Theme, IconProvider

WHITE_1BIT = 255
WHITE_RGB = (255, 255, 255)

class BaseDisplayManager:
    def __init__(self, driver, profile: OledProfile, theme: Theme):
        self.driver = driver
        self.profile = profile
        self.theme = theme

        self.width = getattr(driver, "width", 128)
        self.height = getattr(driver, "height", 64)

        image_mode = getattr(self.profile, "image_mode", None) or getattr(self.theme, "image_mode", "1")

        self.image = Image.new(image_mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        self.font_small = self.theme.load_font(self.theme.font_small)
        self.font       = self.theme.load_font(self.theme.font_regular)
        self.font_large = self.theme.load_font(self.theme.font_large)

        self._icon_provider = IconProvider(image_mode, self.theme.statusbar_icon, self.theme.icon_pack)
        self.icons: Dict[str, Image.Image] = {}

        self._last_stats: Dict = {}
        self.statusbar = None

        status_h = self.profile.statusbar_icon + (2 if self.profile.statusbar_icon <= 8 else 6)
        self.statusbar_height = status_h
        self.content_pad = 4
        self.content_left   = 0 + self.content_pad
        self.content_top    = status_h + self.content_pad
        self.content_right  = self.width - 1 - self.content_pad
        self.content_bottom = self.height - 1 - self.content_pad
        self.content_width  = max(0, self.content_right - self.content_left + 1)
        self.content_height = max(0, self.content_bottom - self.content_top + 1)

    def _background_color(self):
        return self.theme.background

    def color(self):
        return self.theme.foreground

    def begin(self, stats: Dict):
        self._last_stats = stats
        self.clear()

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), fill=self._background_color())

    def show(self):
        self.driver.show(self.image)

    def draw_status_bar(self, statuses: Dict):
        if self.statusbar:
            self.statusbar.draw(self, statuses)

    def line_height(self, font: ImageFont.ImageFont, extra: int = 2) -> int:
        try:
            bbox = font.getbbox("Ag")
            h = bbox[3] - bbox[1]
        except Exception:
            h = getattr(font, "size", 12)
        return int(h + extra)

    def _clamp_rect(self, x0, y0, x1, y1):
        X0 = max(0, min(self.width - 1, int(x0)))
        Y0 = max(0, min(self.height - 1, int(y0)))
        X1 = max(0, min(self.width - 1, int(x1)))
        Y1 = max(0, min(self.height - 1, int(y1)))
        if X1 < X0 or Y1 < Y0:
            return None
        return (X0, Y0, X1, Y1)

    def rect_safe(self, xy, *, outline=None, fill=None, width=1):
        r = self._clamp_rect(*xy)
        if not r:
            return
        if fill is not None:
            self.draw.rectangle(r, fill=fill)
        if outline is not None:
            self.draw.rectangle(r, outline=outline, width=width)

    def text_ellipsis(self, text: str, max_w: int, font) -> str:
        if self.draw.textlength(text, font=font) <= max_w:
            return text
        ell = "…"; ell_w = self.draw.textlength(ell, font=font)
        if ell_w > max_w:
            return ""
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.draw.textlength(text[:mid], font=font) + ell_w <= max_w:
                lo = mid + 1
            else:
                hi = mid
        return text[:max(0, lo-1)] + ell

    def draw_text_row(self, row_idx: int, text: str, *, font=None, fill=None, pad_left: int = 0) -> int:
        font = font or self.font
        fill = fill if fill is not None else self.color()
        lh = self.line_height(font)
        y = self.content_top + row_idx * lh
        if y > self.content_bottom:
            return y
        max_w = max(0, self.content_width - pad_left)
        txt = self.text_ellipsis(text, max_w, font)
        self.draw.text((self.content_left + pad_left, y), txt, font=font, fill=fill)
        return y + lh

    def _get_icon(self, name: str):
        ic = self.icons.get(name)
        if ic is None:
            ic = self._icon_provider.get(name)
            if ic:
                self.icons[name] = ic
        return ic
