from __future__ import annotations
import asyncio
import re
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class LogAnalysisResult(BaseModel):
    component: str
    status: str = "OK"
    file_count: int = 0
    error_samples: list[str] = Field(default_factory=list)

def _analyze_logs_sync(log_dir: Path, patterns: list[str], lookback_hours: int) -> LogAnalysisResult:
    status = "OK"
    error_samples = []
    file_count = 0
    now = datetime.now()
    time_threshold = now - timedelta(hours=lookback_hours)

    if not log_dir.exists():
        return LogAnalysisResult(component=log_dir.name, status="ERROR", error_samples=["Log directory not found."])

    rx_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    for log_file in log_dir.glob("**/*"):
        if not log_file.is_file():
            continue
        
        mtime_dt = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime_dt < time_threshold:
            continue
            
        file_count += 1
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    for rx in rx_patterns:
                        if rx.search(line):
                            status = "WARN"
                            error_samples.append(f"[{log_file.name}] {line.strip()}")
                            if len(error_samples) >= 10:
                                break
                    if len(error_samples) >= 10:
                        break
        except Exception:
            continue

    return LogAnalysisResult(
        component=log_dir.name,
        status=status,
        file_count=file_count,
        error_samples=error_samples
    )

class LogCollector:
    async def analyze_directory(self, log_dir: Path, patterns: list[str], lookback_hours: int) -> LogAnalysisResult:
        return await asyncio.to_thread(_analyze_logs_sync, log_dir, patterns, lookback_hours)