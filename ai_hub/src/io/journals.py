from __future__ import annotations
import subprocess

def run_journalctl(unit: str, *, since: str, min_priority: str) -> str:
    cmd = ["journalctl","-u",unit,"--since",since,"-p",f"{min_priority}..emerg","-o","short-iso"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout or ""
