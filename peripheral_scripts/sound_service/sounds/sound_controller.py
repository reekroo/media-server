#!/usr/bin/env python3

import socket
import os
import sys
import json

sys.path.append('/home/reekroo/peripheral_scripts')
from sounds.libs.buzzer_player import BuzzerPlayer
from sounds.configs import melodies
from utils.logger import setup_logger

log = setup_logger('SoundController', '/home/reekroo/peripheral_scripts/logs/sounds.log')
SOCKET_FILE = "/tmp/buzzer.sock"

def main():
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    player = BuzzerPlayer()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    log.info("[SoundController] Starting Sound Service...")
    
    try:
        server.bind(SOCKET_FILE)
        server.listen(5)

        log.info(f"[SoundController] Listening for commands on {SOCKET_FILE}")

        while True:
            connection, _ = server.accept()
            try:
                command_data = connection.recv(1024).decode()
                if not command_data:
                    continue
                
                log.info(f"[SoundController]  Received command data: '{command_data}'")

                cmd = json.loads(command_data)
                melody_name = cmd.get('melody')
                duration = cmd.get('duration', 0)

                melody_to_play = getattr(melodies, melody_name, None)
                
                if melody_to_play:
                    log.info(f"[SoundController] Passing play command to player: '{melody_name}' for {duration}s.")
                    player.play(melody_to_play, duration)
                else:
                    log.warning(f"Melody '{melody_name}' not found.")
            except Exception as e:
                log.error(f"[SoundController] Error processing command: {e}", exc_info=True)
            finally:
                connection.close()
    finally:
        player.close()
        server.close()

        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
        
        log.info("[SoundController] Sound Service stopped and resources released.")

if __name__ == '__main__':
    main()