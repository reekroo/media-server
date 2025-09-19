from pydantic import BaseModel
from typing import List

class ForecastDay(BaseModel):
    date: str
    max_temp_c: float
    min_temp_c: float
    avg_temp_c: float
    condition: str
    chance_of_rain: int = 0

class ForecastResponse(BaseModel):
    location_name: str
    daily_forecast: List[ForecastDay]

class HistoricalHour(BaseModel):
    time: str
    temp_c: float
    condition: str
    wind_kph: float

class HistoricalResponse(BaseModel):
    location_name: str
    date: str
    hourly_data: List[HistoricalHour]