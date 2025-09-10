from pydantic import BaseModel

class DailyConfig(BaseModel):
    weather_json: str ="/run/monitors/weather/latest.json"
    quakes_json: str ="/run/monitors/earthquakes/last7d.json"
    language: str = "en"
    include_quakes: bool = True