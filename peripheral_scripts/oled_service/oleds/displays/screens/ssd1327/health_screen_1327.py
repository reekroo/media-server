#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G

class HealthScreen1327(BaseScreen):
    """
    Health (SSD1327):
      • Заголовок
      • CPU temp (с оценкой OK/WARN/HOT)
      • NVMe temp (если есть)
      • Throttling (YES/NO/строка)
      • Core V — только если низкое
      • Пустая строка
      • Итоговый статус-бокс на всю ширину: OK / HOT / THR / UV
    """
    HANDLES_BACKGROUND = True

    # Пороговые значения (можешь подстроить под свою систему)
    CPU_WARN = 70.0
    CPU_CRIT = 85.0
    NVME_WARN = 65.0
    NVME_CRIT = 80.0
    VOLT_MIN = 4.75  # ниже — считаем undervoltage

    def _grade_temp(self, t: float, warn: float, crit: float) -> str:
        if t >= crit: return "HOT"
        if t >= warn: return "WARN"
        return "OK"

    def _boolish(self, v) -> bool | None:
        # нормализуем разные форматы throttling: True/False, "YES"/"NO", "0"/"1", "Undervoltage detected", etc.
        if v is None: return None
        if isinstance(v, bool): return v
        s = str(v).strip().lower()
        if s in ("no", "false", "0", "none", "ok"): return False
        if s in ("yes", "true", "1"): return True
        # если пришла строка с текстом про undervoltage/throttled — считаем True
        if any(k in s for k in ("under", "volt", "throttl", "cap")):
            return True
        return None

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

        # --- входные данные ---
        cpu_t  = float(stats.get('temp', 0) or 0.0)
        nvme_t = float(stats.get('nvme_temp', 0) or 0.0)
        volt   = float(stats.get('core_voltage', 0) or 0.0)
        thr_raw = stats.get('throttling', None)   # может быть bool/строка
        thr = self._boolish(thr_raw)

        # --- заголовок ---
        row = 0
        row = G.text_row(cv, dm, row, "Health", font=dm.font_small, fill=c)

        # --- CPU temp ---
        cpu_grade = self._grade_temp(cpu_t, self.CPU_WARN, self.CPU_CRIT)
        row = G.text_row(cv, dm, row, f"CPU {cpu_t:.0f}°  {cpu_grade}", font=dm.font, fill=c)

        # --- NVMe temp (если валидное значение > 0) ---
        nvme_line_shown = False
        if nvme_t > 0:
            nvme_grade = self._grade_temp(nvme_t, self.NVME_WARN, self.NVME_CRIT)
            row = G.text_row(cv, dm, row, f"NVMe {nvme_t:.0f}°  {nvme_grade}", font=dm.font, fill=c)
            nvme_line_shown = True

        # --- Throttling ---
        if thr is True:
            thr_text = "Throttling YES"
        elif thr is False:
            thr_text = "Throttling NO"
        else:
            # если пришла информативная строка — покажем как есть, иначе N/A
            thr_str = str(thr_raw) if thr_raw not in (None, "", "0") else "N/A"
            thr_text = f"Throttling {thr_str}"
        row = G.text_row(cv, dm, row, thr_text, font=dm.font, fill=c)

        # --- Core Voltage: показываем ТОЛЬКО если низкое ---
        uv = volt > 0 and volt < self.VOLT_MIN
        if uv:
            row = G.text_row(cv, dm, row, f"Core V {volt:.1f}V LOW", font=dm.font, fill=c)

        # --- пустая строка ---
        row = G.text_row(cv, dm, row, "", font=dm.font, fill=c)

        # --- итоговый статус ---
        # приоритет: троттлинг -> undervoltage -> горячо -> ок
        if thr is True:
            summary = "THR"
        elif uv:
            summary = "UV"
        else:
            hot_any = (cpu_t >= self.CPU_CRIT) or (nvme_t >= self.NVME_CRIT if nvme_line_shown else False)
            warn_any = (cpu_t >= self.CPU_WARN) or (nvme_t >= self.NVME_WARN if nvme_line_shown else False)
            if hot_any:
                summary = "HOT"
            elif warn_any:
                summary = "WARN"
            else:
                summary = "OK"

        row = self._status_box(cv, dm, row, summary, rows=2)
        dm.show()
