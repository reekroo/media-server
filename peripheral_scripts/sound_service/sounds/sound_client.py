#!/usr/bin/env python3

import socket
import json

SOCKET_FILE = "/tmp/buzzer.sock"

def play_sound(melody_name: str, duration: int = 0, wait: bool = False):
    if not isinstance(melody_name, str) or not melody_name:
        print("Error: melody_name must be a non-empty string.")
        return

    command = {
        "melody": melody_name,
        "duration": duration,
        "wait": wait
    }
    
    client = None
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_FILE)
        client.sendall(json.dumps(command).encode('utf-8'))

        if wait:
            client.recv(1024)

    except socket.error as e:
        print(f"Could not connect to sound service to play '{melody_name}': {e}")
    finally:
        if client:
            client.close()