from __future__ import annotations
from typing import Any, Dict, Optional
from datetime import date, datetime
import json

from .base import ToolSpec
from mcp.context import AppContext
from mcp.services.geocoding_client import GeocodingSocketClient
from mcp.services.weather_client import WeatherSocketClient

def _parse_date_from_iso_string(date_str: Optional[str]) -> date:
    if not date_str:
        return date.today()
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return date.today()

async def _exec_weather(app: AppContext, args: Dict[str, Any]) -> str:
    location_name = args.get("location")
    date_str = args.get("date")

    geocoder = GeocodingSocketClient(app.settings)
    coords = await geocoder.get_coords_for_city(location_name)
    if not coords:
        return f"Sorry, I could not find the location: {location_name}"

    requested_date = _parse_date_from_iso_string(date_str)

    weather_client = WeatherSocketClient(app.settings)
    weather_data = await weather_client.get_weather(
        lat=coords[0], lon=coords[1], requested_date=requested_date
    )

    if isinstance(weather_data, dict) and "error" in weather_data:
        return weather_data.get("error", "Failed to get weather data.")
    
    if not weather_data:
        return "Failed to get weather data from all providers."
    
    summarization_prompt = (
        f"You are a weather assistant. A user asked for the weather in '{location_name}' for the date {requested_date.strftime('%Y-%m-%d')}. "
        "Based ONLY on the following JSON data, provide a concise, natural language answer. Respond in the user's original language.\n\n"
        f"Data:\n{json.dumps(weather_data, indent=2, ensure_ascii=False)}"
    )

    final_answer = await app.ai_service.agent.generate(summarization_prompt)
    return final_answer

TOOL = ToolSpec(
    name="get_weather",
    description=(
        "Get the current weather or a future forecast for a specific location. "
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "location": { "type": "string", "description": "The city and state/country, e.g., 'Berlin, Germany'."},
            "date": {
                "type": "string",
                "format": "date",
                "description": (
                    "The date of interest in YYYY-MM-DD format. You must convert any user-provided relative "
                    "dates (like 'today' or 'tomorrow') into this absolute format."
                )
            }
        },
        "required": ["location"],
    },
    execute=_exec_weather,
)