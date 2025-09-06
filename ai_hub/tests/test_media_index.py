from src.io.media_index import snapshot, diff
from pathlib import Path

def test_diff_empty():
    assert diff({}, {}) == []
