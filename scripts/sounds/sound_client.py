#!/usr/bin/env python3

import socket
import json

SOCKET_FILE = "/tmp/buzzer.sock"

def play_sound(melody_name: str, duration: int = 0):
    """
    Отправляет команду на проигрывание мелодии (и опционально длительность)
    в главный сервис звука.
    """
    if not isinstance(melody_name, str) or not melody_name:
        print("Error: melody_name must be a non-empty string.")
        return
    
    # Создаем словарь с командой
    command = {
        "melody": melody_name,
        "duration": duration
    }
    
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_FILE)
        # Отправляем JSON-строку
        client.sendall(json.dumps(command).encode('utf-8'))
    except socket.error as e:
        # Эта ошибка будет видна в логах сервиса, который вызвал sound_client
        print(f"Could not connect to sound service to play '{melody_name}': {e}")
    finally:
        if 'client' in locals():
            client.close()