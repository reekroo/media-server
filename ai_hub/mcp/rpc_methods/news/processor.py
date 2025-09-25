from typing import Any, List

from .models import SectionParams
from ...context import AppContext
from functions.feeds.feed_collector import FeedCollector, FeedItem

def create_section_params(
    sec_name: str, 
    section_config: Any, 
    global_cfg: Any, 
    count_override: int | None
) -> SectionParams:
    urls = []
    fetch_limit = global_cfg.fetch_limit
    section_limit = count_override if count_override is not None else global_cfg.section_limit

    if isinstance(section_config, list):
        urls = section_config
    elif isinstance(section_config, dict):
        urls = section_config.get("urls", [])
        fetch_limit = section_config.get("fetch_limit", global_cfg.fetch_limit)
        if count_override is None:
            section_limit = section_config.get("section_limit", global_cfg.section_limit)
            
    return SectionParams(
        name=sec_name,
        urls=urls,
        fetch_limit=fetch_limit,
        section_limit=section_limit
    )


class NewsSectionProcessor:
    def __init__(self, app: AppContext, global_cfg: Any, params: SectionParams):
        self.app = app
        self.cfg = global_cfg
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
        return await self.app.ai_service.digest(kind=self.cfg.ai_topic, params=ai_params)

    def _render_template(self, summary: str) -> str:
        return self.cfg.render_template.format(section=self.params.name.capitalize(), summary=summary)