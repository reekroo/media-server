#!/usr/bin/env python3
from __future__ import annotations
from math import ceil
from typing import Sequence, Optional
from .canvas import Canvas

def base_lh(dm) -> int:
    return Canvas._line_height(dm.font)

def text_row(cv, dm, row: int, text: str, *, font=None, fill=None, pad_left: int=0) -> int:
    font = font or dm.font
    BASE_LH = base_lh(dm)
    y_row = cv.top + row * BASE_LH
    lh = Canvas._line_height(font)
    y_txt = y_row + max(0, (BASE_LH - lh) // 2)
    if y_txt <= cv.bottom:
        cv.text(cv.left + pad_left, y_txt, text, font=font, fill=fill or dm.color(), max_w=cv.width - pad_left)
    return row + 1

def fit_text(cv, font, variants: Sequence[str]) -> str:
    for s in variants:
        if cv.draw.textlength(s, font=font) <= cv.width:
            return s
    return variants[-1] if variants else ""

def bar_row(
    cv, dm, row: int, value01: float, *,
    height: int = 12, gap_above: int = 2, gap_below: int = 2,
    min_rows: int = 1, fg=None, bg=None, border=None, width: Optional[int] = None
) -> int:
    BASE_LH = base_lh(dm)
    y_bar = cv.top + row * BASE_LH + gap_above
    w = min(width or 120, cv.width)
    v = max(0.0, min(1.0, float(value01)))
    if y_bar <= cv.bottom:
        h = min(height, max(0, cv.bottom - y_bar))
        if h >= 1:
            cv.bar(cv.left, y_bar, w, h, v, fg=fg or dm.color(), bg=bg or dm.theme.background, border=border or dm.color())
    rows_used = max(min_rows, ceil((gap_above + height + gap_below) / BASE_LH))
    return row + rows_used

def spark_row(
    cv, dm, row: int, values: Sequence[float], *,
    height: int = 12, gap_above: int = 4, gap_below: int = 0,
    min_rows: int = 1, fg=None, width: Optional[int] = None
) -> int:
    BASE_LH = base_lh(dm)
    y_sp = cv.top + row * BASE_LH + gap_above
    w = min(width or 120, cv.width)
    if y_sp <= cv.bottom and height > 0:
        cv.sparkline(cv.left, y_sp, w, min(height, max(0, cv.bottom - y_sp)), list(values), fg=fg or dm.color())
    rows_used = max(min_rows, ceil((gap_above + height + gap_below) / BASE_LH))
    return row + rows_used

def blank_row(row: int, n: int = 1) -> int:
    return row + max(0, int(n))

def box_row(
    cv, dm, row: int, text: str, *,
    rows: int = 2, pad: int = 2, radius: int = 8, font=None
) -> int:
    
    color   = dm.color()
    BASE_LH = base_lh(dm)
    y0 = cv.top + row * BASE_LH
    y1 = min(cv.bottom, cv.top + (row + rows) * BASE_LH - 1)
    x0 = cv.left
    x1 = cv.right - 1

    try:
        cv.draw.rounded_rectangle([x0, y0, x1, y1], outline=color, width=1, radius=radius)
    except Exception:
        cv.draw.rectangle([x0, y0, x1, y1], outline=color, width=1)

    inner_w = max(0, (x1 - x0 + 1) - pad * 2)
    inner_h = max(0, (y1 - y0 + 1) - pad * 2)

    f = font or dm.font
    tw = cv.draw.textlength(text, font=f)
    if tw > inner_w:
        f = dm.font_small
        tw = cv.draw.textlength(text, font=f)

    lh = Canvas._line_height(f)
    tx = x0 + pad + max(0, (inner_w - tw) // 2)
    ty = y0 + pad + max(0, (inner_h - lh) // 2)

    cv.text(tx, ty, text, font=f, fill=color)
    return row + rows

def spark_area(
    cv, dm, row: int, series_list: Sequence[Sequence[float]], *,
    colors: Optional[Sequence] = None,
    height: int = 24,
    gap_above: int = 2,
    gap_below: int = 0,
    min_rows: int = 2,
    width: Optional[int] = None,
):
    BASE_LH = base_lh(dm)
    y = cv.top + row * BASE_LH + gap_above
    w = min(width or 120, cv.width)
    h = min(height, max(0, cv.bottom - y))

    if y <= cv.bottom and h > 0:
        for i, seq in enumerate(series_list):
            fg = (colors[i] if (colors and i < len(colors)) else dm.color())
            cv.sparkline(cv.left, y, w, h, list(seq), fg=fg)

    rows_used = max(min_rows, ceil((gap_above + height + gap_below) / BASE_LH))
    return row + rows_used