import socket
import os
import json
import threading
import logging
from dataclasses import asdict

from services.on_demand_earthquake_service import OnDemandEarthquakeService

class OnDemandSocketServer: 
    def __init__(self, socket_path: str, service: OnDemandEarthquakeService, logger: logging.Logger):
        self._socket_path = socket_path
        self._service = service
        self._log = logger
        self._server_socket = None
        self._stop_event = threading.Event()
        self._server_thread = None

    def _handle_client(self, conn: socket.socket):
        with conn:
            try:
                request_data = conn.recv(1024).decode('utf-8')
                if not request_data:
                    return

                self._log.info(f"On-demand server: Received request: {request_data}")
                request = json.loads(request_data)
                
                lat = request.get("lat")
                lon = request.get("lon")
                days = request.get("days", 1)

                if lat is None or lon is None:
                    raise ValueError("'lat' or 'lon' key is missing in request")

                events = self._service.get_earthquakes_for_coords(
                    lat=float(lat), lon=float(lon), days=int(days)
                )

                events_as_dict = [asdict(event) for event in events]
                response = {"status": "success", "data": events_as_dict}

                conn.sendall(json.dumps(response).encode('utf-8'))
                self._log.info(f"On-demand server: Sent {len(events)} events for coords ({lat}, {lon}).")

            except (json.JSONDecodeError, ValueError) as e:
                self._log.error(f"On-demand server: Invalid request from client: {e}")
                error_response = {"status": "error", "message": "Invalid JSON request. 'lat' and 'lon' are required."}
                conn.sendall(json.dumps(error_response).encode('utf-8'))
            except Exception as e:
                self._log.error(f"On-demand server: Error handling client: {e}", exc_info=True)

    def _server_loop(self):
        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(self._socket_path)
        os.chmod(self._socket_path, 0o666)
        self._server_socket.listen(10)
        self._server_socket.settimeout(1.0)
        self._log.info(f"On-demand earthquake socket server listening on {self._socket_path}")

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
                self._log.error(f"On-demand server: Error accepting connection: {e}")

        self._log.info("On-demand socket server loop stopped.")

    def start(self):
        self._thread = threading.Thread(target=self._server_loop, name="OnDemandEarthquakeServer", daemon=True)
        self._thread.start()

    def stop(self):
        self._log.info(f"Stopping On-demand earthquake server...")
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except OSError:
                pass