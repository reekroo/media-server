#!/usr/bin/env python3

import socket
import os
import sys
import json
import time
import traceback

sys.path.append('/home/reekroo/scripts')
from sounds.libs.buzzer_player import BuzzerPlayer
from sounds.configs import melodies
from common.logger import setup_logger

log = setup_logger('SoundController', '/home/reekroo/scripts/logs/sounds.log')
SOCKET_FILE = "/tmp/buzzer.sock"

def main():
    if os.path.exists(SOCKET_FILE):
        try:
            os.remove(SOCKET_FILE)
        except FileNotFoundError:
            pass
        except PermissionError:
            print(f"Warning: cannot remove {SOCKET_FILE}, check permissions")

    player = BuzzerPlayer()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    log.info("Starting Sound Service...")
    try:
        server.bind(SOCKET_FILE)
        server.listen(5)
        log.info(f"Listening for commands on {SOCKET_FILE}")

        while True:
            connection, _ = server.accept()
            try:
                command_data = connection.recv(1024).decode()
                if not command_data:
                    continue

                log.info(f"Received command data: '{command_data}'")
                cmd = json.loads(command_data)
                melody_name = cmd.get('melody')
                duration = cmd.get('duration', 0)

                melody_to_play = getattr(melodies, melody_name, None)

                if melody_to_play:
                    log.info(f"Found melody '{melody_name}'. Playing for {duration}s.")
  
                    if duration > 0:
                        start_time = time.time()
                        while time.time() - start_time < duration:
                            player.play(melody_to_play)
                    else:
                        player.play(melody_to_play)
                    log.info(f"Finished playing '{melody_name}'.")
                else:
                    log.warning(f"Melody '{melody_name}' not found.")
            except Exception as e:
                log.error(f"Error processing command: {e}", exc_info=True)
            finally:
                connection.close()

    except KeyboardInterrupt:
        log.info("\nShutting down Sound Service.")
    finally:
        player.close()
        server.close()
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
        log.info("Sound Service stopped and resources released.")

if __name__ == '__main__':
    main()