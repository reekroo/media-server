#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G

class HealthScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    CPU_WARN=70.0
    CPU_CRIT=85.0
    NVME_WARN=65.0
    NVME_CRIT=80.0
    VOLT_MIN=4.75

    def _grade(self,t,w,c): return "HOT" if t>=c else "WARN" if t>=w else "OK"

    def _boolish(self,v):
        if v is None: return None
        if isinstance(v,bool): return v
        s=str(v).strip().lower()
        if s in ("no","false","0","ok"): return False
        if s in ("yes","true","1"): return True
        if any(k in s for k in ("under","volt","throttl","cap")): return True
        return None

    def draw(self, dm, stats):
        c=dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv=Canvas.from_display(dm)

        cpu=float(stats.get('temp',0) or 0.0)
        nvme=float(stats.get('nvme_temp',0) or 0.0)
        volt=float(stats.get('core_voltage',0) or 0.0)
        thr_raw=stats.get('throttling'); thr=self._boolish(thr_raw)

        row=0
        row=G.text_row(cv,dm,row,"Health",font=dm.font,fill=c)
        row=G.text_row(cv,dm,row,f"CPU {cpu:.0f}°  {self._grade(cpu,self.CPU_WARN,self.CPU_CRIT)}",font=dm.font_small,fill=c)
        if nvme>0:
            row=G.text_row(cv,dm,row,f"NVMe {nvme:.0f}°  {self._grade(nvme,self.NVME_WARN,self.NVME_CRIT)}",font=dm.font_small,fill=c)

        thr_text="Throttling "+("YES" if thr is True else "NO" if thr is False else (str(thr_raw) if thr_raw not in (None,"") else "N/A"))
        row=G.text_row(cv,dm,row,thr_text,font=dm.font_small,fill=c)

        uv = volt>0 and volt<self.VOLT_MIN
        if uv:
            row=G.text_row(cv,dm,row,f"Core V {volt:.1f}V LOW",font=dm.font_small,fill=c)

        row=G.blank_row(row,1)

        if thr is True: summary="THR"
        elif uv: summary="UV"
        elif (cpu>=self.CPU_CRIT) or (nvme>=self.NVME_CRIT if nvme>0 else False): summary="HOT"
        elif (cpu>=self.CPU_WARN) or (nvme>=self.NVME_WARN if nvme>0 else False): summary="WARN"
        else: summary="OK"

        row=G.box_row(cv,dm,row,summary,rows=2)
        dm.show()
