from typing import Optional
from .base_message_target_config import MessageTargetConfig

class DailyConfig(MessageTargetConfig):
    generate_image: Optional[bool] = False

    weather_json: str ="/run/monitors/weather/latest.json"
    quakes_json: str ="/run/monitors/earthquakes/last7d.json"
    
    language: str = "en"
    include_quakes: bool = True