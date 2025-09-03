import socket
import json
import logging
from .base import ILocationProvider

class SocketLocationProvider(ILocationProvider):
    def __init__(self, socket_path: str, logger: logging.Logger):
        self._socket_path = socket_path
        self._log = logger
        self._log.info(f"Initialized socket location provider for path: {socket_path}")

    def get_location(self) -> dict | None:
        self._log.info("Attempting to get location from external location_service...")
        
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                client_socket.connect(self._socket_path)
                data = client_socket.recv(1024)
            
            if data:
                location = json.loads(data.decode('utf-8'))
                self._log.info(f"Successfully received location from service: {location}")
                return location
            else:
                self._log.warning("Received no data from location service socket.")
                return None
            
        except (socket.error, FileNotFoundError, json.JSONDecodeError, socket.timeout) as e:
            self._log.warning(f"Failed to get location from service socket: {e}")
            return None