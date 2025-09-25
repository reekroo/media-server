from pydantic import BaseModel

class ScheduleEntry(BaseModel):
    enabled: bool = True
    cron: str