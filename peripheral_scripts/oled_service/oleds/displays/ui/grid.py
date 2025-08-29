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