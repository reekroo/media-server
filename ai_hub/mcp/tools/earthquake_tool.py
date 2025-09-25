from __future__ import annotations
from typing import Any, Dict
import json

from .base import ToolSpec
from mcp.context import AppContext
from mcp.services.geocoding_client import GeocodingSocketClient
from mcp.services.earthquake_client import EarthquakeSocketClient

async def _exec_earthquakes(app: AppContext, args: Dict[str, Any]) -> str:
    location = args.get("location")
    days = args.get("days", 1)

    geocoder = GeocodingSocketClient(app.settings)
    coords = await geocoder.get_coords_for_city(location)
    if not coords:
        return f"Sorry, I could not find the location: {location}"

    earthquake_client = EarthquakeSocketClient(app.settings)
    events_data = await earthquake_client.get_earthquakes(
        lat=coords[0], lon=coords[1], days=int(days)
    )

    if not events_data or isinstance(events_data, dict) and "error" in events_data:
        return events_data.get("error", "Failed to get earthquake data.")
    
    if not events_data:
        return f"No significant earthquakes were recorded near {location} in the last {days} day(s)."

    user_question = f"What were the recent earthquakes near {location} in the last {days} day(s)?"
    
    summarization_prompt = (
        "You are a seismology assistant. Based on the user's question and the following JSON data of recent "
        "earthquake events, provide a concise, natural language summary. "
        "Mention the number of events, the strongest one, and any notable patterns. Respond in the user's original language.\n\n"
        f"User's Question: '{user_question}'\n\n"
        f"Earthquake Events Data (JSON):\n{json.dumps(events_data, indent=2, ensure_ascii=False)}"
    )

    final_answer = await app.ai_service.agent.generate(summarization_prompt)
    return final_answer

TOOL = ToolSpec(
    name="get_earthquake_events",
    description=(
        "Get recent earthquake events for a specific location. "
        "Useful for questions like 'were there any earthquakes in Turkey?' or 'what were the recent quakes near Izmir?'"
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state/country, e.g., 'Izmir, Turkey'. Must be provided by the user."
            },
            "days": {
                "type": "integer",
                "description": "The number of past days to check for events. Defaults to 1."
            }
        },
        "required": ["location"],
        "additionalProperties": False,
    },
    execute=_exec_earthquakes,
)