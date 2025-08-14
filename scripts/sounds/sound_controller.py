#!/usr/bin/env python3

import socket
import os
import sys
import traceback

# Добавляем путь к корневой папке скриптов
sys.path.append('/home/reekroo/scripts')
from sounds.libs.buzzer_player import BuzzerPlayer
from sounds.configs import melodies

SOCKET_FILE = "/tmp/buzzer.sock"

def main():
    # Убедимся, что старый файл сокета удален
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    player = BuzzerPlayer()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    print("Starting Sound Service...")
    try:
        server.bind(SOCKET_FILE)
        server.listen(5)
        print(f"Listening for commands on {SOCKET_FILE}")

        while True:
            connection, _ = server.accept()
            try:
                command = connection.recv(1024).decode()
                if not command:
                    continue

                print(f"Received command: '{command}'")
                
                # Находим мелодию по имени в вашем модуле melodies
                melody_to_play = getattr(melodies, command, None)
                
                if melody_to_play:
                    player.play(melody_to_play)
                    print(f"Played melody: '{command}'")
                else:
                    print(f"Warning: Melody '{command}' not found.")
            except Exception as e:
                print(f"Error processing command: {e}")
                traceback.print_exc()
            finally:
                connection.close()

    except KeyboardInterrupt:
        print("\nShutting down Sound Service.")
    finally:
        player.close()
        server.close()
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
        print("Sound Service stopped and resources released.")

if __name__ == '__main__':
    main()