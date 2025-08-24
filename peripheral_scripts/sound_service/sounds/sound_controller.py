import socket
import os
import json
import stat

from .libs.buzzer_player import BuzzerPlayer
from .configs import melodies
from .configs.configs import SOUND_SOCKET, SOUNDS_LOG_FILE

from utils.logger import setup_logger

log = setup_logger("SoundController", SOUNDS_LOG_FILE)

def main():
    if os.path.exists(SOUND_SOCKET):
        os.remove(SOUND_SOCKET)

    player = BuzzerPlayer()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    log.info("[SoundController] Starting Sound Service…")

    try:
        server.bind(SOUND_SOCKET)
        server.listen(5)
        os.chmod(SOUND_SOCKET, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        log.info(f"[SoundController] Listening for commands on {SOUND_SOCKET}")

        while True:
            connection, _ = server.accept()
            try:
                raw = connection.recv(1024)
                if not raw:
                    connection.sendall(b"NOK")
                    continue

                try:
                    cmd = json.loads(raw.decode())
                except json.JSONDecodeError:
                    log.warning("[SoundController] Bad JSON: %r", raw)
                    connection.sendall(b"NOK")
                    continue

                melody_name = cmd.get("melody")
                duration = float(cmd.get("duration", 0))
                wait_flag = bool(cmd.get("wait", False))

                melody_to_play = melodies.ALL_MELODIES.get(melody_name)
                if not melody_to_play:
                    log.warning("[SoundController] Unknown melody: %r", melody_name)
                    connection.sendall(b"NOK")
                    continue

                log.info("[SoundController] Play request: name=%s duration=%s wait=%s", melody_name, duration, wait_flag)

                player.play(melody_to_play, duration)
                if wait_flag:
                    player.wait() 
                    connection.sendall(b"OK")
                else:
                    connection.sendall(b"ACK")

            except Exception as e:
                log.error("[SoundController] Error: %s", e, exc_info=True)
                try:
                    connection.sendall(b"NOK")
                except Exception:
                    pass
            finally:
                try:
                    connection.close()
                except Exception:
                    pass
    finally:
        try:
            player.close()
        finally:
            try:
                server.close()
            finally:
                if os.path.exists(SOUND_SOCKET):
                    os.remove(SOUND_SOCKET)
        log.info("[SoundController] Sound Service stopped and resources released.")

if __name__ == "__main__":
    main()
