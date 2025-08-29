#!/usr/bin/env python3
from ..base import BaseScreen
from ...ui.canvas import Canvas
from ...ui import grid as G

class DockerScreen1327(BaseScreen):
    HANDLES_BACKGROUND = True

    def _status_label(self, stats)->str:
        raw=(stats.get("docker_status") or "").strip().lower()
        if bool(stats.get("status_docker", False)): return "RUN"
        if raw in ("restarting","restart"): return "RESTART"
        if raw in ("exited","stopped","dead"): return "STOP"
        return raw.upper() if raw else "N/A"

    def draw(self, dm, stats):
        c=dm.color()
        dm.clear(); dm.draw_status_bar(stats)
        cv=Canvas.from_display(dm)

        label=self._status_label(stats)

        restarts=stats.get("docker_restarts")
        try: restarts=int(restarts)
        except Exception: restarts=0

        exit_code=stats.get("docker_exit_code", stats.get("exit_code"))
        try: exit_code=int(exit_code)
        except Exception: exit_code="N/A"

        row=0
        row=G.text_row(cv,dm,row,"Docker",font=dm.font,fill=c)
        row=G.text_row(cv,dm,row,f"Status {label}",font=dm.font_small,fill=c)
        row=G.text_row(cv,dm,row,f"Restarts {restarts}",font=dm.font_small,fill=c)
        row=G.text_row(cv,dm,row,f"Exit {exit_code}",font=dm.font_small,fill=c)
        row=G.blank_row(row,1)
        row=G.box_row(cv,dm,row,label,rows=2)
        dm.show()
