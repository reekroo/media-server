import requests
from typing import Dict, Any

class HttpClient:
    def get(self, url: str, params: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()