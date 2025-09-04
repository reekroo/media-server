import socket
import os
import json
import time
import threading
import logging
from pathlib import Path
from typing import List

from providers.base import ILocationProvider

class LocationController:
    def __init__(self, providers: List[ILocationProvider], logger: logging.Logger, socket_path: Path, update_interval: int):
        self._socket_path = socket_path
        self._providers = providers
        self.log = logger
        self._update_interval = update_interval
        self._current_location = None
        self._server_socket = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def _update_location_loop(self):
        self.log.info("Location update thread started.")
        
        while not self._stop_event.is_set():
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
                    self._current_location = new_location
                    self.log.info(f"Location updated to: {self._current_location}.")
                else:
                    self.log.error("Failed to determine location from all providers.")

            self.log.info(f"Next location update in {self._update_interval} seconds.")
            self._stop_event.wait(self._update_interval)
        
        self.log.info("Location update thread stopped.")

    def _serve_clients(self):
        try:
            self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._server_socket.bind(str(self._socket_path))
            self._server_socket.listen(5)
            self.log.info("Location service is listening on %s", self._socket_path)
        except OSError as e:
            self.log.critical(f"Failed to bind to socket {self._socket_path}: {e}")
            self._stop_event.set()
            return

        while not self._stop_event.is_set():
            try:
                self._server_socket.settimeout(1.0)
                conn, _ = self._server_socket.accept()
                with conn:
                    with self._lock:
                        location_to_send = self._current_location
                    
                    if location_to_send:
                        self.log.info("Client connected. Sending: %s", location_to_send)
                        conn.sendall(json.dumps(location_to_send).encode('utf-8'))
                    else:
                        self.log.warning("Client connected, but no location data is available yet.")
            except socket.timeout:
                continue
            except socket.error as e:
                self.log.error(f"Socket error during accept: {e}")
                break

    def run(self):
        if self._socket_path.exists():
            try:
                self._socket_path.unlink()
            except OSError as e:
                self.log.error(f"Error removing old socket file {self._socket_path}: {e}")

        update_thread = threading.Thread(target=self._update_location_loop, daemon=True)
        update_thread.start()
        
        try:
            self._serve_clients()
        
        except KeyboardInterrupt:
            self.log.info("Shutdown signal (KeyboardInterrupt) received.")
        
        finally:
            self.log.info("Initiating shutdown...")
            self._stop_event.set()

            if self._server_socket:
                self._server_socket.close()

            update_thread.join(timeout=5)
            if update_thread.is_alive():
                self.log.warning("Location update thread did not stop in time.")
            
            if self._socket_path.exists():
                try:
                    self._socket_path.unlink()
                except OSError as e:
                    self.log.error(f"Error removing socket file during shutdown: {e}")
            
            self.log.info("Location service has been shut down.")