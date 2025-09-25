import requests
import logging
from typing import Any, Dict, Optional

log = logging.getLogger("WeatherMonitor")

class HttpClient:
    def get_json(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 10) -> Any:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            log.error(f"HTTP error occurred: {http_err}")
            log.error(f"Response status code: {http_err.response.status_code}")
            log.error(f"Response content: {http_err.response.text}")
            return None
            
        except requests.exceptions.RequestException as req_err:
            log.error(f"Request error occurred: {req_err}")
            return None