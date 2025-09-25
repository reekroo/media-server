from typing import List, Tuple, Iterable, Set
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

from .feed_models import FeedItem

def normalize_url_for_dedupe(url: str) -> str:
    if not url: return ""
    try:
        u = urlparse(url)
        query = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not k.lower().startswith(("utm_", "fbclid", "gclid"))]
        return urlunparse((u.scheme.lower(), u.netloc.lower(), u.path, u.params, urlencode(query, doseq=True), ""))
    except Exception:
        return url.strip().lower()

def to_iso8601(dt: datetime | None) -> str | None:
    if not dt: return None
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()

def extract_published(entry: dict) -> Tuple[datetime | None, str | None]:
    for key in ("published_parsed", "updated_parsed"):
        if tm := entry.get(key):
            try:
                return (dt := datetime(*tm[:6], tzinfo=timezone.utc)), to_iso8601(dt)
            except Exception: pass
    for key in ("published", "updated"):
        if s := entry.get(key):
            try:
                return (dt := parsedate_to_datetime(s)), to_iso8601(dt)
            except Exception: pass
    return None, None

def extract_summary(entry: dict) -> str | None:
    summary = entry.get("summary") or entry.get("description")
    if isinstance(summary, str):
        return summary.strip()
    
    content = entry.get("content")
    if isinstance(content, list) and content:
        first_content = content[0]
        if isinstance(first_content, dict):
            return first_content.get("value", "").strip()
    return None

def dedupe_items(items: Iterable[FeedItem]) -> List[FeedItem]:
    seen: Set[str] = set()
    out: List[FeedItem] = []
    for it in items:
        key = normalize_url_for_dedupe(it.link) or (it.title.strip().lower() if it.title else "")
        if not key or key in seen: continue
        seen.add(key)
        out.append(it)
    return out

def sort_items_by_date_desc(items: List[FeedItem]) -> List[FeedItem]:
    def key_fn(it: FeedItem):
        if not it.published: return datetime.min.replace(tzinfo=timezone.utc)
        try:
            return datetime.fromisoformat(it.published)
        except (ValueError, TypeError):
            return datetime.min.replace(tzinfo=timezone.utc)
    return sorted(items, key=key_fn, reverse=True)