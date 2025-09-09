import aiohttp
import asyncio
import feedparser
import logging
from dataclasses import dataclass
from typing import List, Optional

log = logging.getLogger(__name__)

@dataclass
class FeedItem:
    title: str
    link: str
    published: str | None
    summary: str | None

class FeedCollector:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session: Optional[aiohttp.ClientSession] = session

    async def __aenter__(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _fetch_and_parse_feed(self, url: str) -> List[FeedItem]:
        try:
            HEADERS = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124 Safari/537.36"
                ),
                "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
            }
            async with self._session.get(url, headers=HEADERS, timeout=15) as response:
                response.raise_for_status()
                text = await response.text()
                parsed = feedparser.parse(text)

                items: List[FeedItem] = []
                for entry in parsed.entries[:50]:
                    summary = (
                        entry.get("summary")
                        or entry.get("description")
                        or (
                            entry.get("content", [{}])[0].get("value")
                            if isinstance(entry.get("content"), list) and entry.get("content")
                            else None
                        )
                    )
                    
                    if isinstance(summary, str):
                        summary = summary.strip()
                        if len(summary) > 2000:
                            summary = summary[:2000] + "…"

                    items.append(
                        FeedItem(
                            title=entry.get("title", "") or "",
                            link=entry.get("link", "") or "",
                            published=entry.get("published"),
                            summary=summary,
                        )
                    )

                log.info("Successfully fetched %s items from %s", len(items), url)
                return items

        except Exception as e:
            log.error("Failed to fetch or parse feed %s. Error: %s", url, str(e), exc_info=True)
            return []

    async def collect(self, urls: List[str], max_items: int = 30) -> List[FeedItem]:
        if not self._session:
            self._session = aiohttp.ClientSession()

        tasks = [self._fetch_and_parse_feed(url) for url in urls]
        results = await asyncio.gather(*tasks)
        all_items = [item for sublist in results for item in sublist]
        return all_items[:max_items]
