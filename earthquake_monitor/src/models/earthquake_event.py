from dataclasses import dataclass

@dataclass(frozen=True)
class EarthquakeEvent:
    event_id: str
    magnitude: float
    place: str
    latitude: float
    longitude: float
    timestamp: int