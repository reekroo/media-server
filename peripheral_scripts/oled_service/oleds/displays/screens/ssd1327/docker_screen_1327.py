#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G


class DockerScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def _status_label(self, stats) -> str:
        """Нормализация статуса в короткий бейдж."""
        raw = (stats.get("docker_status") or "").strip().lower()
        is_run = bool(stats.get("status_docker", False))
        if is_run:
            return "RUN"
        if raw in ("restarting", "restart"):
            return "RESTART"
        if raw in ("exited", "stopped", "dead"):
            return "STOP"
        return raw.upper() if raw else "N/A"

    def _status_box(self, cv, dm, row: int, text: str, *, rows: int = 2, pad_y: int = 2):
        """
        Рисует бокс на всю ширину контентной области, с центрированным текстом статуса.
        Возвращает следующий row (на rows вперёд).
        """
        color = dm.color()
        BASE_LH = G.base_lh(dm)
        # область бокса по сетке (rows рядов)
        y0 = cv.top + row * BASE_LH
        h  = max(1, rows * BASE_LH - 2)  # лёгкий внутренний зазор
        y1 = min(cv.bottom, y0 + h)
        x0 = cv.left
        x1 = cv.right

        # рамка по периметру
        try:
            cv.draw.rounded_rectangle([x0, y0, x1, y1], outline=color, width=1, radius=8)
        except Exception:
            cv.draw.rectangle([x0, y0, x1, y1], outline=color, width=1)

        # выбираем шрифт, который точно влезет
        font = dm.font
        tw = cv.draw.textlength(text, font=font)
        if tw > cv.width - 10:  # узко — упадём на small
            font = dm.font_small
            tw = cv.draw.textlength(text, font=font)

        # вертикальная и горизонтальная центровка
        lh = Canvas._line_height(font)
        tx = x0 + max(0, (cv.width - tw) // 2)
        ty = y0 + max(pad_y, (h - lh) // 2)

        cv.text(tx, ty, text, font=font, fill=color)
        return row + rows

    def draw(self, dm, stats):
        c = dm.color()
        dm.clear()
        dm.draw_status_bar(stats)
        cv = Canvas.from_display(dm)

        label = self._status_label(stats)

        # Достаём метрики
        restarts = stats.get("docker_restarts")
        try:
            restarts = int(restarts)
        except Exception:
            restarts = 0

        exit_code = stats.get("docker_exit_code", stats.get("exit_code"))
        try:
            exit_code = int(exit_code)
        except Exception:
            exit_code = "N/A"

        row = 0
        # 1) Docker (заголовок)
        row = G.text_row(cv, dm, row, "Docker", font=dm.font_small, fill=c)
        # 2) Status
        row = G.text_row(cv, dm, row, f"Status {label}", font=dm.font, fill=c)
        # 3) Restarts
        row = G.text_row(cv, dm, row, f"Restarts {restarts}", font=dm.font, fill=c)
        # 4) Exit
        row = G.text_row(cv, dm, row, f"Exit {exit_code}", font=dm.font, fill=c)
        # 5) Пустая строка
        row = G.text_row(cv, dm, row, "", font=dm.font, fill=c)
        # 6) Бокс на всю ширину с центром текста
        row = self._status_box(cv, dm, row, label, rows=2)

        dm.show()
