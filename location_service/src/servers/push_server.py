import socket
import json
import threading
import logging
from pathlib import Path

from services.ip_location_service import IpLocationService

class PushServer:
    def __init__(self, service: IpLocationService, logger: logging.Logger, socket_path: Path):
        self._service = service
        self.log = logger
        self._socket_path = socket_path
        self._server_socket = None
        self._stop_event = threading.Event()
        self._thread = None

    def _handle_client(self, conn: socket.socket):
        with conn:
            location_to_send = self._service.get_cached_location()
            if location_to_send:
                self.log.info("Push server: Client connected. Sending: %s", location_to_send)
                conn.sendall(json.dumps(location_to_send).encode('utf-8'))
            else:
                self.log.warning("Push server: Client connected, but no location data is available yet.")

    def _server_loop(self):
        try:
            self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._server_socket.bind(str(self._socket_path))
            self._server_socket.listen(5)
            self.log.info("Push server is listening on %s", self._socket_path)
        except OSError as e:
            self.log.critical(f"Failed to bind push server to socket {self._socket_path}: {e}")
            return
        
        while not self._stop_event.is_set():
            try:
                self._server_socket.settimeout(1.0)
                conn, _ = self._server_socket.accept()
                self._handle_client(conn)
            except socket.timeout:
                continue
            except socket.error:
                if not self._stop_event.is_set():
                    self.log.error("Push server socket error.")
                break
        
        self.log.info("Push server loop has stopped.")

    def start(self):
        if self._socket_path.exists():
            self._socket_path.unlink()
        self._thread = threading.Thread(target=self._server_loop, name="PushServer", daemon=True)
        self._thread.start()

    def stop(self):
        self.log.info("Stopping Push Server...")
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        if self._socket_path.exists():
            try: self._socket_path.unlink()
            except OSError: pass