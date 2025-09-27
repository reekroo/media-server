from typing import List

from .models import SectionParams
from ...context import AppContext
from functions.feeds.feed_collector import FeedCollector, FeedItem

class NewsSectionProcessor:
    def __init__(self, app: AppContext, ai_topic: str, params: SectionParams):
        self.app = app
        self.ai_topic = ai_topic
        self.params = params

    async def process(self) -> str | None:
        items = await self._fetch_items()
        if not items:
            return None
        
        summary = await self._get_summary(items)
        if not summary:
            return None
            
        return self._render_template(summary)

    async def _fetch_items(self) -> List[FeedItem]:
        if not self.params.urls:
            return []
        async with FeedCollector() as collector:
            return await collector.collect(
                urls=self.params.urls, 
                fetch_limit=self.params.fetch_limit
            )

    async def _get_summary(self, items: List[FeedItem]) -> str | None:
        ai_params = {
            'items': [item.__dict__ for item in items],
            'section': self.params.name,
            'count': self.params.section_limit
        }
        return await self.app.ai_service.digest(kind=self.ai_topic, params=ai_params)

    def _render_template(self, summary: str) -> str:
        return self.params.render_template.format(
            section=self.params.name.capitalize(), 
            summary=summary
        )