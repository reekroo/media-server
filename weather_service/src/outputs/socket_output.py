import socket
import os
import json
import threading
import time

from .base import IOutputStrategy
from models.weather_data import WeatherData
from weather_logger import get_logger

log = get_logger(__name__)

class SocketOutput(IOutputStrategy):
    def __init__(self, socket_path: str):
        self._socket_path = socket_path
        self._server_socket = None
        self._last_json = None
        self._stop = False
        self._accept_thread = None
        self._setup_server()
        self._start_accept_loop()

    def _setup_server(self):
        if os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except Exception:
                pass

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            self._server_socket.bind(self._socket_path)
            try:
                os.chmod(self._socket_path, 0o666)
            except Exception:
                pass

            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
            log.info(f"Listen Socket Path: {self._socket_path}")

        except Exception as e:
            log.error(f"Error socket {self._socket_path}: {e}")
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

    def _start_accept_loop(self):
        if not self._server_socket:
            return

        def _loop():
            log.info("Weather socket accept loop started.")
            while not self._stop:
                try:
                    conn, _ = self._server_socket.accept()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._stop:
                        break
                    log.error(f"Accept error: {e}")
                    time.sleep(0.2)
                    continue

                with conn:
                    try:
                        payload = self._last_json or json.dumps({"status": "no_data"})
                        conn.sendall(payload.encode("utf-8"))
                        log.info("Weather data sent to client.")
                    except Exception as e:
                        log.error(f"Send error: {e}")
            log.info("Weather socket accept loop stopped.")

        self._accept_thread = threading.Thread(
            target=_loop, name="WeatherSocketAccept", daemon=True
        )
        self._accept_thread.start()

    def output(self, data: WeatherData):
        if data is None:
            return
        try:
            self._last_json = json.dumps(data._asdict())
        except Exception:
            try:
                self._last_json = json.dumps(dict(data))
            except Exception as e:
                log.error(f"Serialize weather data failed: {e}")

    def close(self):
        self._stop = True
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        if self._accept_thread and self._accept_thread.is_alive():
            try:
                self._accept_thread.join(timeout=1.0)
            except Exception:
                pass

        try:
            if os.path.exists(self._socket_path):
                os.remove(self._socket_path)
        except Exception:
            pass

        log.info("Socket closed.")