from __future__ import annotations
import re
from typing import Dict, List, Tuple
from .model import UnitStatus, LogEntry, Issue, UnitReport, Level

def _match_patterns(entries: List[LogEntry], patterns: Dict[str, List[str]], max_samples: int = 3) -> Tuple[List[Issue], List[str]]:
    issues: List[Issue] = []
    samples: List[str] = []
    for category, pats in (patterns or {}).items():
        for p in pats:
            rx = re.compile(p, re.IGNORECASE)
            matched = [e.line for e in entries if rx.search(e.line)]
            if matched:
                issues.append(Issue(category=category, pattern=p))
                for m in matched[:max_samples - len(samples)]:
                    samples.append(m)
                if len(samples) >= max_samples:
                    return issues, samples
    return issues, samples

def classify(status: UnitStatus, logs: List[LogEntry], patterns: Dict[str, List[str]], max_restarts: int) -> UnitReport:
    issues, samples = _match_patterns(logs, patterns)
    level: Level = "OK"
    if status.active != "active" or issues:
        level = "WARN"
    if status.active == "failed" or status.restarts > max_restarts:
        level = "FAIL"
    return UnitReport(unit=status.unit, status=status, level=level, issues=issues, samples=samples)