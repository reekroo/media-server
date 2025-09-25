import aiohttp
import asyncio
import feedparser
from typing import List, Optional

from core.logging import setup_logger, LOG_FILE_PATH

from . import feed_utils
from .feed_models import FeedItem

log = setup_logger(__name__, LOG_FILE_PATH)


class FeedCollector:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None, *, conn_limit: int = 20):
        self._external_session = session
        self._internal_session: Optional[aiohttp.ClientSession] = None
        self._conn_limit = conn_limit

    @property
    def _session(self) -> aiohttp.ClientSession:
        session = self._external_session or self._internal_session
        if not session:
            raise RuntimeError("Session not available. Use FeedCollector as an async context manager.")
        return session

    async def __aenter__(self):
        if not self._external_session:
            connector = aiohttp.TCPConnector(limit=self._conn_limit, ssl=False)
            self._internal_session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._internal_session:
            await self._internal_session.close()

    async def _fetch_one(self, url: str, per_feed_fetch_limit: int) -> List[FeedItem]:
        HEADERS = {"User-Agent": "Mozilla/5.0 (...", "Accept": "application/rss+xml,..."}
        try:
            async with self._session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as response:
                response.raise_for_status()
                text = await response.text()
                parsed = feedparser.parse(text)
                
                items: List[FeedItem] = []
                for entry in parsed.entries[:max(1, per_feed_fetch_limit)]:
                    summary = feed_utils.extract_summary(entry)
                    if summary and len(summary) > 2000:
                        summary = summary[:2000] + "…"

                    _, iso_published = feed_utils.extract_published(entry)
                    items.append(FeedItem(
                        title=(entry.get("title", "") or "").strip(),
                        link=(entry.get("link", "") or "").strip(),
                        published=iso_published,
                        summary=summary,
                    ))
                log.debug("Fetched %s items from %s", len(items), url)
                return items
        except aiohttp.client_exceptions.ClientConnectorDNSError:
            log.warning(f"DNS Error for {url}")
            return []
        except aiohttp.ClientResponseError as e:
            log.warning(f"HTTP Error for {url}: status={e.status}")
            return []
        except asyncio.TimeoutError:
            log.warning(f"Timeout fetching {url}")
            return []
        except Exception:
            log.exception("Unexpected error fetching or parsing feed %s", url)
            return []

    async def collect(
        self,
        urls: List[str],
        fetch_limit: int = 30,
        *,
        per_feed_fetch_limit: int = 50,
        dedupe: bool = True,
        sort_by_date: bool = True,
    ) -> List[FeedItem]:
        if not urls: return []

        log.info("Creating %s fetch tasks...", len(urls))
        tasks = [
            asyncio.create_task(self._fetch_one(url, per_feed_fetch_limit), name=f"fetch-{url[:50]}")
            for url in urls
        ]
        
        results_from_tasks = await asyncio.gather(*tasks)
        log.info("All fetch tasks completed.")

        all_items = [item for sublist in results_from_tasks for item in sublist]
        if dedupe: all_items = feed_utils.dedupe_items(all_items)
        if sort_by_date: all_items = feed_utils.sort_items_by_date_desc(all_items)

        final_items = all_items[:fetch_limit] if fetch_limit > 0 else all_items
        log.info("Aggregated %s items (from %s urls, limit=%s)", len(final_items), len(urls), fetch_limit)
        return final_items