import httpx
import json
import logging
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)

class HttpClient:
    async def get_json(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 20) -> Any:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()

                if not response.text.strip():
                    log.warning(f"Received an empty response from {url}")
                    return None
                
                try:
                    return response.json()
                except json.JSONDecodeError as json_err:
                    log.error(f"Failed to decode JSON from {url}. Error: {json_err}")
                    log.error(f"Response text snippet: '{response.text[:500]}'")
                    return None

        except httpx.HTTPStatusError as http_err:
            log.error(f"HTTP error occurred: {http_err}")
            if http_err.response:
                log.error(f"Response status code: {http_err.response.status_code}")
                log.error(f"Response content: {http_err.response.text}")
            return None
            
        except httpx.RequestError as req_err:
            log.error(f"Request error occurred: {req_err}")
            return None

    async def get_text(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 20) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response.text
            
        except httpx.HTTPStatusError as http_err:
            log.error(f"HTTP error occurred: {http_err}")
            if http_err.response:
                log.error(f"Response status code: {http_err.response.status_code}")
                log.error(f"Response content: {http_err.response.text}")
            return None
        
        except httpx.RequestError as req_err:
            log.error(f"Request error occurred: {req_err}")
            return None