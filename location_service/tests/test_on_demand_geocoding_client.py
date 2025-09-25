import socket
import json
import sys

SOCKET_PATH = "/tmp/geocoding_service.sock"

def main():
    city = "Paris"
    request_payload = {"city_name": city}

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            print(f"Connecting to {SOCKET_PATH}...")
            client.connect(SOCKET_PATH)
            
            print(f"Sending request for city '{city}': {request_payload}")
            client.sendall(json.dumps(request_payload).encode('utf-8'))

            response_data = client.recv(1024).decode('utf-8')
            
            print("\n--- RESPONSE ---")
            response_json = json.loads(response_data)
            print(json.dumps(response_json, indent=2))
            print("----------------")

    except FileNotFoundError:
        print(f"Error: Socket file not found at {SOCKET_PATH}. Is the main application running?", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()