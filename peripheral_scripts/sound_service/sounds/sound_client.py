import socket
import json

from .configs.configs import SOUND_SOCKET

def play_sound(melody_name: str, duration: int = 0, wait: bool = False, timeout: float | None = 5.0) -> bool:

    if not isinstance(melody_name, str) or not melody_name:
        print("Error: melody_name must be a non-empty string.")
        return False

    command = {
        "melody": melody_name,
        "duration": duration,
        "wait": wait,
    }

    client = None
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        if timeout is not None:
            client.settimeout(timeout)

        client.connect(SOUND_SOCKET)
        client.sendall(json.dumps(command).encode("utf-8"))

        if wait:
            data = client.recv(1024)
            return data == b"OK"
        else:
            data = client.recv(1024)
            return data in (b"ACK", b"OK")

    except (socket.timeout, OSError) as e:
        print(f"Could not connect to sound service to play '{melody_name}': {e}")
        return False
    
    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass
