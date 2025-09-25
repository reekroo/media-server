import requests
from typing import Any, Dict, Optional

class HttpClient:
    def get_json(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 10) -> Any:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()