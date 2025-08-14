#!/usr/bin/env python3

import socket

SOCKET_FILE = "/tmp/buzzer.sock"

def play_sound(melody_name: str):
    """
    Отправляет команду на проигрывание мелодии в главный сервис звука.
    """
    if not isinstance(melody_name, str) or not melody_name:
        print("Error: melody_name must be a non-empty string.")
        return
        
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_FILE)
        client.sendall(melody_name.encode())
    except socket.error as e:
        # Логируем ошибку, если сервис звука не доступен
        print(f"Could not connect to sound service to play '{melody_name}': {e}")
    finally:
        if 'client' in locals():
            client.close()