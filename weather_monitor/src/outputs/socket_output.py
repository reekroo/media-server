import socket
import os
import json
import threading
import time
import logging

from .base import IOutputStrategy
from models.weather_data import WeatherData

class SocketOutput(IOutputStrategy):
    def __init__(self, socket_path: str, logger: logging.Logger):
        self._socket_path = socket_path
        self._log = logger
        self._server_socket = None
        self._last_json = json.dumps({"status": "initializing"})
        self._stop = False
        self._accept_thread = None
        
        self._setup_server()
        self._start_accept_loop()

    def _setup_server(self):
        if os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except OSError as e:
                self._log.warning(f"Could not remove stale socket file {self._socket_path}: {e}")

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            self._server_socket.bind(self._socket_path)
            os.chmod(self._socket_path, 0o666)
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
            self._log.info(f"Socket server is listening on: {self._socket_path}")
        except Exception as e:
            self._log.error(f"Failed to bind or listen on socket {self._socket_path}: {e}")
            if self._server_socket:
                self._server_socket.close()
            self._server_socket = None

    def _start_accept_loop(self):
        if not self._server_socket:
            return
        
        self._accept_thread = threading.Thread(
            target=self._accept_connections, name="WeatherSocketAccept", daemon=True
        )
        self._accept_thread.start()

    def _accept_connections(self):
        self._log.info("Socket accept loop started.")
        while not self._stop:
            try:
                conn, _ = self._server_socket.accept()
                with conn:
                    try:
                        payload = self._last_json
                        conn.sendall(payload.encode("utf-8"))
                        self._log.info(f"Sent {len(payload)} bytes of weather data to a socket client.")
                    except Exception as e:
                        self._log.error(f"Error sending data to client: {e}")
            except socket.timeout:
                continue
            except Exception as e:
                if self._stop:
                    break
                self._log.error(f"Error accepting connection: {e}")
                time.sleep(0.2)
        self._log.info("Socket accept loop stopped.")

    def output(self, data: WeatherData):
        if data is None:
            return
        try:
            self._last_json = json.dumps(data._asdict())
        except Exception as e:
            self._log.error(f"Failed to serialize weather data: {e}")

    def close(self):
        self._log.info("Closing socket output...")
        self._stop = True
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        if self._accept_thread and self._accept_thread.is_alive():
            self._accept_thread.join(timeout=1.0)

        if os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except Exception:
                pass
        self._log.info("Socket output closed.")