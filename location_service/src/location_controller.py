import socket
import os
import json
import time
import threading

from typing import List
from configs import SOCKET_FILE, UPDATE_INTERVAL_SECONDS
from providers.base import ILocationProvider
from location_logger import get_logger

log = get_logger(__name__)

class LocationController:
    def __init__(self, providers: List[ILocationProvider]):
        self._socket_path = SOCKET_FILE
        self._providers = providers
        self._current_location = None
        self._server_socket = None
        self._lock = threading.Lock() # <-- Замок для безопасного доступа к данным из разных потоков
        self._stop_event = threading.Event()

    def _update_location_loop(self):
        log.info("Location update thread started.")
        
        while not self._stop_event.is_set():
            new_location = None
            for provider in self._providers:
                location = provider.determine_location()
                if location:
                    new_location = location
                    break
            
            with self._lock:
                self._current_location = new_location
            
            log.info(f"Location updated to: {self._current_location}. Waiting for {UPDATE_INTERVAL_SECONDS}s.")

            self._stop_event.wait(UPDATE_INTERVAL_SECONDS)
        
        log.info("Location update thread stopped.")

    def _serve_clients(self):
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(self._socket_path)
        self._server_socket.listen(5)

        log.info("Location service is listening on %s", self._socket_path)
        
        while not self._stop_event.is_set():
            try:
                conn, _ = self._server_socket.accept()
                with conn:
                    with self._lock:
                        location_to_send = self._current_location
                    
                    if location_to_send:
                        log.info("Client connected. Sending: %s", location_to_send)
                        conn.sendall(json.dumps(location_to_send).encode('utf-8'))
                    else:
                        log.warning("Client connected, but no location data is available yet.")
            except socket.error:
                break

    def run(self):
        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)
            
        update_thread = threading.Thread(target=self._update_location_loop, daemon=True)
        update_thread.start()
        
        try:
            self._serve_clients()
        
        except KeyboardInterrupt:
            log.info("Shutdown signal received.")
        
        finally:
            self._stop_event.set()
            update_thread.join(timeout=5)

            if self._server_socket:
                self._server_socket.close()
            
            if os.path.exists(self._socket_path):
                os.remove(self._socket_path)
            
            log.info("Location service has been shut down.")