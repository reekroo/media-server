import requests
from typing import Any

class HttpClient:
    def get_json(self, url: str, timeout: int = 10) -> Any:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()