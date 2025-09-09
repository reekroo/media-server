from src.digests.sys.rules import classify
from src.digests.sys.model import UnitStatus, LogEntry

def test_classify_ok():
    st = UnitStatus(unit="x.service", active="active", restarts=0)
    rep = classify(st, [], {}, max_restarts=3)
    assert rep.level == "OK"
