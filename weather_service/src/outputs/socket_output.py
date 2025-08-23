import socket
import os
import json

from .base import IOutputStrategy
from models.weather_data import WeatherData
from weather_logger import get_logger

log = get_logger(__name__)

class SocketOutput(IOutputStrategy):
    def __init__(self, socket_path: str):
        self._socket_path = socket_path
        self._server_socket = None
        self._setup_server()

    def _setup_server(self):
        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)
        
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            self._server_socket.bind(self._socket_path)
            self._server_socket.listen(1)
            log.info(f"Listen Socket Path: {self._socket_path}"
                     )
        except Exception as e:
            log.error(f"Error socket {self._socket_path}: {e}")
            self._server_socket = None

    def output(self, data: WeatherData):
        if not self._server_socket:
            log.error("Socket is not run")
            return
            
        log.info("Waiting for the connection...")
        try:
            conn, addr = self._server_socket.accept()
            with conn:
                log.info(f"Client connection. Sending data...")
                json_data = json.dumps(data._asdict())
                conn.sendall(json_data.encode('utf-8'))
                log.info("Data was sent.")
        except Exception as e:
            log.error(f"Error socket: {e}")

    def close(self):
        if self._server_socket:
            self._server_socket.close()
            os.remove(self._socket_path)
            log.info("Socket closed.")