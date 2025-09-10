from __future__ import annotations
import asyncio
from typing import List

from .model import UnitStatus, LogEntry

async def _run_async(cmd: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode('utf-8').strip()

async def get_unit_status(unit: str) -> UnitStatus:
    active_task = _run_async(["systemctl", "is-active", unit])
    show_task = _run_async(["systemctl", "show", unit, "-p", "NRestarts", "-p", "FragmentPath"])
    
    active, show = await asyncio.gather(active_task, show_task)
    
    active = active or "unknown"
    restarts = 0
    fragment_path = None
    
    for line in show.splitlines():
        if line.startswith("NRestarts="):
            try:
                restarts = int(line.split("=", 1)[1].strip() or "0")
            except (ValueError, IndexError):
                restarts = 0
        elif line.startswith("FragmentPath="):
            fragment_path = line.split("=", 1)[1].strip() or None
            
    return UnitStatus(unit=unit, active=active, restarts=restarts, fragment_path=fragment_path)

async def get_unit_logs(unit: str, lookback: str, min_priority: str) -> List[LogEntry]:
    cmd = ["journalctl", "-u", unit, "--since", lookback, "-p", f"{min_priority}..emerg", "-o", "short-iso"]
    out = await _run_async(cmd)
    
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