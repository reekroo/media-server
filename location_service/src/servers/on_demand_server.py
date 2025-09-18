import socket
import json
import threading
import logging
from pathlib import Path

from services.geocoding_service import GeocodingService

class OnDemandGeocodingServer:
    def __init__(self, service: GeocodingService, logger: logging.Logger, socket_path: Path):
        self._socket_path = socket_path
        self._service = service
        self.log = logger
        self._server_socket = None
        self._stop_event = threading.Event()
        self._thread = None

    def _handle_client(self, conn: socket.socket):
        with conn:
            try:
                request_data = conn.recv(1024).decode('utf-8')
                if not request_data:
                    return

                self.log.info(f"On-demand geocoding: Received request: {request_data}")
                request = json.loads(request_data)
                city_name = request.get("city_name")

                if not city_name:
                    raise ValueError("'city_name' is missing in request")

                location_data = self._service.geocode_city(city_name)
                
                if not location_data or location_data.get('status') != 'success':
                    response = json.dumps({"status": "error", "message": f"Could not find coordinates for '{city_name}'."}).encode('utf-8')
                else:
                    response = json.dumps(location_data).encode('utf-8')
                
                conn.sendall(response)
                self.log.info(f"Sent response for city '{city_name}'.")

            except (json.JSONDecodeError, ValueError) as e:
                self.log.error(f"Invalid request from client: {e}")
                error_response = json.dumps({"status": "error", "message": "Invalid request format."}).encode('utf-8')
                conn.sendall(error_response)
            except Exception as e:
                self.log.error(f"Error handling geocoding client: {e}", exc_info=True)

    def _server_loop(self):
        try:
            self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._server_socket.bind(str(self._socket_path))
            self._server_socket.listen(10)
            self._server_socket.settimeout(1.0)
            self.log.info(f"On-demand geocoding server listening on {self._socket_path}")
        except OSError as e:
            self.log.critical(f"Failed to bind to socket {self._socket_path}: {e}")
            return

        while not self._stop_event.is_set():
            try:
                conn, _ = self._server_socket.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self._stop_event.is_set():
                    break
                self.log.error(f"Error accepting connection: {e}")

        self.log.info("On-demand geocoding server loop stopped.")
        
    def start(self):
        if self._socket_path.exists():
            self._socket_path.unlink()
        self._thread = threading.Thread(target=self._server_loop, name="OnDemandGeocodingServer", daemon=True)
        self._thread.start()

    def stop(self):
        self.log.info("Closing on-demand geocoding server...")
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._socket_path.exists():
            try:
                self._socket_path.unlink()
            except OSError:
                pass