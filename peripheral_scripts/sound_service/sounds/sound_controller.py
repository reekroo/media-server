#!/usr/bin/env python3
import os
import stat
import json
import socket

from .libs.buzzer_player import BuzzerPlayer
from .configs.melodies import ALL_MELODIES
from .configs.configs import SOUND_SOCKET, SOUNDS_LOG_FILE

from utils.logger import setup_logger

log = setup_logger("SoundController", SOUNDS_LOG_FILE)


def _safe_send(conn: socket.socket, payload: bytes) -> None:
    try:
        conn.sendall(payload)
    except (BrokenPipeError, ConnectionResetError, OSError):
        pass


def _prepare_socket(path: str) -> socket.socket:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass

    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(path)
    
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    srv.listen(5)
    return srv


def main() -> None:
    server = None
    player = None
    try:
        server = _prepare_socket(SOUND_SOCKET)
        log.info("[SoundController] Starting Sound Service…")
        log.info("[SoundController] Listening for commands on %s", SOUND_SOCKET)

        player = BuzzerPlayer()

        while True:
            try:
                connection, _ = server.accept()
            except OSError as e:
                log.error("[SoundController] accept() failed: %s", e, exc_info=True)
                continue

            try:
                try:
                    raw = connection.recv(4096)
                except OSError as e:
                    log.warning("[SoundController] recv() error: %s", e)
                    connection.close()
                    continue

                if not raw:
                    connection.close()
                    continue

                try:
                    req = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    log.warning("[SoundController] Bad JSON: %r", raw)
                    _safe_send(connection, b"NOK")
                    connection.close()
                    continue

                melody_name = req.get("melody") or req.get("name")
                duration = float(req.get("duration") or 0.0)
                wait_flag = bool(req.get("wait"))

                melody = ALL_MELODIES.get(melody_name)
                if not melody:
                    log.warning("[SoundController] Unknown melody: %r", melody_name)
                    _safe_send(connection, b"NOK")
                    connection.close()
                    continue

                log.info("[SoundController] Play request: name=%s duration=%s wait=%s",
                         melody_name, duration, wait_flag)

                try:
                    player.play(melody, duration)
                    if wait_flag:
                        player.wait()
                        _safe_send(connection, b"OK")
                    else:
                        _safe_send(connection, b"ACK")
                except Exception as e:
                    log.error("[SoundController] Error while playing: %s", e, exc_info=True)
                    _safe_send(connection, b"NOK")

            finally:
                try:
                    connection.close()
                except Exception:
                    pass

    except KeyboardInterrupt:
        log.info("[SoundController] Interrupted by user.")
    except Exception as e:
        log.error("[SoundController] Fatal error: %s", e, exc_info=True)
    finally:
        try:
            if player is not None:
                player.close()
        except Exception:
            pass
        try:
            if server is not None:
                server.close()
        except Exception:
            pass
        try:
            if os.path.exists(SOUND_SOCKET):
                os.remove(SOUND_SOCKET)
        except Exception:
            pass

        log.info("[SoundController] Sound Service stopped and resources released.")


if __name__ == "__main__":
    main()
