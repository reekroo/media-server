import logging
import threading
from typing import List, Optional

from providers.base import ILocationProvider

class IpLocationService:
    def __init__(self, providers: List[ILocationProvider], logger: logging.Logger):
        self._providers = providers
        self.log = logger
        self._lock = threading.Lock()
        self._cached_location: Optional[dict] = None

    def get_cached_location(self) -> Optional[dict]:
        with self._lock:
            return self._cached_location

    def update_location(self) -> None:
        self.log.info("IP Location Service: Attempting to update location...")
        new_location = None
        for provider in self._providers:
            try:
                location = provider.determine_location()
                if location:
                    new_location = location
                    self.log.info(f"Location successfully determined by {provider.__class__.__name__}.")
                    break
            except Exception as e:
                self.log.error(f"Error in provider {provider.__class__.__name__}: {e}", exc_info=True)
        
        with self._lock:
            if new_location:
                self._cached_location = new_location
                self.log.info(f"IP-based location updated to: {self._cached_location}.")
            else:
                self.log.error("Failed to determine location from all IP providers.")