from __future__ import annotations
import subprocess
from typing import List
from .model import UnitStatus, LogEntry

def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

def get_unit_status(unit: str) -> UnitStatus:
    active = _run(["systemctl", "is-active", unit]) or "unknown"
    show = _run(["systemctl", "show", unit, "-p", "NRestarts", "-p", "FragmentPath"])
    restarts = 0
    fragment_path = None
    for line in show.splitlines():
        if line.startswith("NRestarts="):
            try:
                restarts = int(line.split("=", 1)[1].strip() or "0")
            except ValueError:
                restarts = 0
        elif line.startswith("FragmentPath="):
            fragment_path = line.split("=", 1)[1].strip() or None
    return UnitStatus(unit=unit, active=active, restarts=restarts, fragment_path=fragment_path)

def get_unit_logs(unit: str, lookback: str, min_priority: str) -> List[LogEntry]:
    cmd = ["journalctl", "-u", unit, "--since", lookback, "-p", f"{min_priority}..emerg", "-o", "short-iso"]
    out = _run(cmd)
    entries: List[LogEntry] = []
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        ts = None
        parts = ln.split()
        if len(parts) >= 2 and parts[0][0].isdigit():
            ts = f"{parts[0]} {parts[1]}"
        entries.append(LogEntry(ts=ts, priority=None, line=ln))
    return entries
