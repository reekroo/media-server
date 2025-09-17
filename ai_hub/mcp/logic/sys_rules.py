import re
from typing import Dict, List, Tuple

from functions.sys.models import UnitStatus, LogEntry, Issue, UnitReport, Level, Incident

def _match_patterns(entries: List[LogEntry], patterns: Dict[str, List[str]]) -> Tuple[List[Issue], List[str]]:
    issues: List[Issue] = []
    samples: List[str] = []
    
    for category, pats in (patterns or {}).items():
        for p_text in pats:
            if any(re.search(p_text, e.line, re.IGNORECASE) for e in entries):
                issues.append(Issue(category=category, pattern=p_text))
                samples.extend(
                    e.line for e in entries if re.search(p_text, e.line, re.IGNORECASE)
                )

    unique_samples = sorted(list(set(samples)))
    return issues, unique_samples[:3]

def classify(status: UnitStatus, logs: List[LogEntry], patterns: Dict[str, List[str]], max_restarts: int) -> UnitReport:
    issues, samples = _match_patterns(logs, patterns)
    
    level: Level = "OK"
    if status.active != "active" or issues:
        level = "WARN"
    if status.active == "failed" or status.restarts > max_restarts:
        level = "FAIL"
        
    return UnitReport(unit=status.unit, status=status, level=level, issues=issues, samples=samples)

def determine_overall_level(reports: List[UnitReport]) -> Level:
    if any(r.level == "FAIL" for r in reports):
        return "FAIL"
    if any(r.level == "WARN" for r in reports):
        return "WARN"
    return "OK"

def create_incident_from_report(report: UnitReport) -> Incident:
    incident_id = f"{report.unit.replace('.', '_')}_{report.level}_{report.status.restarts}"
    return Incident(
        id=incident_id,
        unit=report.unit,
        level=report.level,
        reason=report.issues,
        restarts=report.status.restarts,
        active=report.status.active,
        samples=report.samples,
    )