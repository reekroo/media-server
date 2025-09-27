from typing import Optional
from .message_target_config import MessageTargetConfig

class DailyConfig(MessageTargetConfig):
    destination_language: Optional[str] = None
    generate_image: Optional[bool] = False

    weather_json: str ="/run/monitors/weather/latest.json"
    quakes_json: str ="/run/monitors/earthquakes/last7d.json"
    
    language: str = "en"
    include_quakes: bool = True