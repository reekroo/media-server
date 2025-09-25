import socket
import os
import json
import threading
import logging
from datetime import date, datetime
from dataclasses import asdict

from services.on_demand_weather_service import OnDemandWeatherService
from models.weather_data import WeatherData

class OnDemandSocketServer: 
    def __init__(self, socket_path: str, on_demand_service: OnDemandWeatherService, logger: logging.Logger):
        self._socket_path = socket_path
        self._on_demand_service = on_demand_service
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
                
                date_str = request.get("date")
                requested_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

                if lat is None or lon is None:
                    raise ValueError("'lat' or 'lon' key is missing in request")

                weather_data = self._on_demand_service.get_weather_for_coords_and_date(
                    lat=float(lat), lon=float(lon), requested_date=requested_date
                )

                if weather_data:
                    if isinstance(weather_data, WeatherData):
                        payload = weather_data._asdict()
                    else:
                        payload = weather_data
                    
                    response = {"status": "success", "data": payload}
                else:
                    response = {"status": "error", "message": "Failed to get weather data from all providers."}

                conn.sendall(json.dumps(response).encode('utf-8'))
                self._log.info(f"On-demand server: Sent response for coords ({lat}, {lon}) on {requested_date}.")

            except (json.JSONDecodeError, ValueError) as e:
                self._log.error(f"On-demand server: Invalid request from client: {e}")
                error_response = {"status": "error", "message": "Invalid JSON. Required: 'lat', 'lon'. Optional: 'date' (YYYY-MM-DD)."}
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
        self._log.info(f"On-demand weather socket server listening on {self._socket_path}")

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
        self._server_thread = threading.Thread(target=self._server_loop, name="OnDemandWeatherServerLoop", daemon=True)
        self._server_thread.start()

    def close(self):
        self._log.info("Closing on-demand socket server...")
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2.0)
        if os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except OSError:
                pass
        self._log.info("On-demand socket server closed.")