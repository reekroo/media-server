import socket
import json
import logging
from .base import ILocationProvider

class SocketLocationProvider(ILocationProvider):
    def __init__(self, logger: logging.Logger, socket_path: str, timeout: int = 5):
        self._log = logger
        self._socket_path = socket_path
        self._timeout = timeout

    def get_location(self) -> dict | None:
        self._log.info(f"Attempting to get location from socket: {self._socket_path}...")
        
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(self._timeout)
                client_socket.connect(self._socket_path)
                
                data = client_socket.recv(1024)
                
                if data:
                    location = json.loads(data.decode('utf-8'))
                    self._log.info("Successfully received location from service: %s", location)
                    return location
            return None
            
        except (socket.error, FileNotFoundError, json.JSONDecodeError, socket.timeout) as e:
            self._log.warning(f"Failed to get location from service socket: {e}")
            return None