from dataclasses import dataclass

@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    published: str | None
    summary: str | None