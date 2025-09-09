from __future__ import annotations
import asyncio

async def run_journalctl_async(unit: str, *, since: str, min_priority: str) -> str:

    cmd = ["journalctl", "-u", unit, "--since", since, "-p", f"{min_priority}..emerg", "-o", "short-iso"]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    if stderr:
        pass
        
    return stdout.decode('utf-8').strip()