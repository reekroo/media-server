from __future__ import annotations
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

_EP = re.compile(r"(?i)\bS(\d{1,2})E(\d{2})\b")

_TAG_CATEGORIES = {
    "quality": r"480p|720p|1080p|2160p|4K",
    "source": r"WEB[-_. ]?DL|WEB[-_. ]?Rip|Blu[-_. ]?Ray|IMAX",
    "codec": r"x264|x265|H\.?264|H\.?265",
    "platform": r"AMZN|NF|HMAX|DSNP",
    "group": r"RGzRutracker|Rarbg|YTS|NTb",
}
_TAG = re.compile(r"(?i)\b(" + "|".join(_TAG_CATEGORIES.values()) + r")\b")

_DOTS = re.compile(r"[._]+")
_TRIM = re.compile(r"\s{2,}")

def normalize_release(raw: str) -> Tuple[str, str | None, str | None]:
    s = raw.strip().rsplit(".", 1)[0]
    
    se_match = _EP.search(s)
    se = f"S{int(se_match.group(1)):02d}E{int(se_match.group(2)):02d}" if se_match else None

    tags_found = [match.group(0).replace("WEB DL", "WEB-DL").replace("WEB Rip", "WEB-Rip") for match in _TAG.finditer(s)]
    tags = " ".join(sorted(set(tags_found))) if tags_found else None

    s_cleaned = _EP.sub("", _TAG.sub("", s))
    title = _DOTS.sub(" ", s_cleaned).strip(" -._")
    title_capitalized = " ".join(w.capitalize() if not w.isupper() else w for w in title.split())
    title_final = _TRIM.sub(" ", title_capitalized)

    return (title_final or raw), se, tags

def compact_se_range(eps: Iterable[str]) -> str | None:
    eps = sorted(set(eps))
    if not eps:
        return None
        
    first_match = _EP.fullmatch(eps[0])
    if not first_match:
        return ", ".join(eps)
        
    season = int(first_match.group(1))
    first = last = int(first_match.group(2))
    
    for e in eps[1:]:
        m = _EP.fullmatch(e)
        if not (m and int(m.group(1)) == season):
            return ", ".join(eps)
        
        cur = int(m.group(2))
        if cur == last + 1:
            last = cur
        else:
            return ", ".join(eps)
            
    if first == last:
        return f"S{season:02d}E{first:02d}"
    return f"S{season:02d}E{first:02d}–E{last:02d}"

def group_new_titles(raw_titles: Iterable[str]) -> List[str]:
    grouped = defaultdict(lambda: {"eps": set(), "tags": set()})
    
    for raw in (raw_titles or []):
        title, se, tags = normalize_release(raw)
        if se:
            grouped[title]["eps"].add(se)
        if tags:
            grouped[title]["tags"].add(tags)

    lines: List[str] = []
    for title, meta in grouped.items():
        se_range = compact_se_range(meta["eps"]) or ""
        all_tags = " ".join(sorted(meta["tags"]))
        
        suffix = f" ({all_tags})" if all_tags else ""
        line = f"{title} — {se_range}{suffix}" if se_range else f"{title}{suffix}"
        lines.append(line)

    return sorted(lines)