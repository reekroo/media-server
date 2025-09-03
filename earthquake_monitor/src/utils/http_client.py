import requests
from typing import Dict, Any

class HttpClient:
    def get(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None, timeout: int = 10) -> requests.Response:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response