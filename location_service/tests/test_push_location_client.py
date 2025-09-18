import socket
import json
import sys

SOCKET_PATH = "/tmp/location_service.sock"

def main():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            print(f"Connecting to {SOCKET_PATH} to get the latest IP-based location...")
            client.connect(SOCKET_PATH)
            response_data = client.recv(1024).decode('utf-8')
            
            print("\n--- IP-BASED LOCATION ---")
            response_json = json.loads(response_data)
            print(json.dumps(response_json, indent=2))
            print("-------------------------")

    except FileNotFoundError:
        print(f"Error: Socket file not found at {SOCKET_PATH}. Is the main application running?", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()