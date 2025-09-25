import socket
import json
import sys
from datetime import date, timedelta

SOCKET_PATH = "/tmp/on_demand_weather.sock"
BUFFER_SIZE = 4096

def main():
    print("--- TEST: FORECAST ---")
    tomorrow = date.today() + timedelta(days=1)
    request_payload = {
        "lat": 51.5074,
        "lon": -0.1278,
        "date": tomorrow.strftime('%Y-%m-%d')
    }

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(15.0)
            client.connect(SOCKET_PATH)

            print(f"-> Sending request: {json.dumps(request_payload)}")
            client.sendall(json.dumps(request_payload).encode('utf-8'))

            response_chunks = []
            while True:
                chunk = client.recv(BUFFER_SIZE)
                if not chunk: break
                response_chunks.append(chunk)
            
            response_data = b''.join(response_chunks).decode('utf-8')

            print("<- Received response:")
            print(json.dumps(json.loads(response_data), indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        print("--------------------\n")

if __name__ == "__main__":
    main()