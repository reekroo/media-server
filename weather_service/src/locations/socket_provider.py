import socket
import json

from .base import ILocationProvider
from configs import LOCATION_SERVICE_SOCKET
from weather_logger import get_logger

log = get_logger(__name__)

class SocketLocationProvider(ILocationProvider):
    def get_location(self) -> dict | None:
        log.info("Attempting to get location from external location_service...")
        
        try:
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(LOCATION_SERVICE_SOCKET)
            
            data = client_socket.recv(1024)
            client_socket.close()
            
            if data:
                location = json.loads(data.decode('utf-8'))
                log.info("Successfully received location from service: %s", location)
                return location
            
        except (socket.error, FileNotFoundError, json.JSONDecodeError, socket.timeout) as e:
            log.warning("Failed to get location from service socket: %s", e)
            return None
        
        return None