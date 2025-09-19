from pydantic import BaseModel

from .schedule_entry_config import ScheduleEntry 

class ScheduleConfig(BaseModel):
    daily_brief: ScheduleEntry | None = None
    dinner_ideas: ScheduleEntry | None = None
    media_digest: ScheduleEntry | None = None
    entertainment: ScheduleEntry | None = None
    gaming_digest: ScheduleEntry | None = None
    news_digest: ScheduleEntry | None = None
    eu_news: ScheduleEntry | None = None
    us_news: ScheduleEntry | None = None
    russian_news: ScheduleEntry | None = None
    belarus_news: ScheduleEntry | None = None
    turkish_news: ScheduleEntry | None = None
    sys_digest: ScheduleEntry | None = None
    docker_digest: ScheduleEntry | None = None
    log_digest: ScheduleEntry | None = None