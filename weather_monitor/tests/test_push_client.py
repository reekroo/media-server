import socket
import json
import sys

SOCKET_PATH = "/tmp/weather_service.sock"

def main():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
            print(f"Connecting to {SOCKET_PATH} to get the latest broadcasted data...")
            client_socket.connect(SOCKET_PATH)
            response_data = client_socket.recv(4096).decode('utf-8')
            
            print("\n--- LATEST WEATHER DATA ---")
            response_json = json.loads(response_data)
            print(json.dumps(response_json, indent=4, ensure_ascii=False))
            print("---------------------------")

    except FileNotFoundError:
        print(f"Error: Socket file not found at {SOCKET_PATH}. Is the main application running?", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()