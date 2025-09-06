from __future__ import annotations
import asyncio
import logging
from typing import List
import aiohttp
import feedparser
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class FeedItem(BaseModel):
    title: str
    summary: str
    link: str

class FeedCollector:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def collect(self, urls: List[str], *, max_items: int | None = None) -> List[FeedItem]:
        tasks = [self._fetch_and_parse_feed(url) for url in urls]
        results_from_feeds = await asyncio.gather(*tasks)
        
        all_items: List[FeedItem] = []
        for feed_items in results_from_feeds:
            all_items.extend(feed_items)
            
        return all_items[:max_items] if max_items else all_items

    async def _fetch_and_parse_feed(self, url: str) -> List[FeedItem]:
        items: List[FeedItem] = []
        try:
            logger.info(f"Fetching feed: {url}")
            async with self._session.get(url, timeout=15) as response:
                response.raise_for_status()
                feed_text = await response.text()
                
            parsed_feed = feedparser.parse(feed_text)
            
            for entry in (parsed_feed.entries or []):
                summary = getattr(entry, "summary", "") or getattr(entry, "subtitle", "")
                item = FeedItem(
                    title=getattr(entry, "title", "No Title"),
                    summary=summary,
                    link=getattr(entry, "link", ""),
                )
                items.append(item)
            logger.info(f"Successfully fetched {len(items)} items from {url}")
        except Exception as e:
            # ИЗМЕНЕНИЕ: Используем exception для полного трейсбека в логах
            logger.exception(f"Failed to fetch or parse feed {url}. Error: {e}")
            
        return items