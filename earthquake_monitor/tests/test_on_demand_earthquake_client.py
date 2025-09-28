import asyncio
import json
import sys

SOCKET_PATH = "/tmp/on_demand_earthquake.sock"

async def main():
    request_payload = {
        "lat": 35.6895,
        "lon": 139.6917,
        "days": 3
    }

    try:
        print(f"Connecting to {SOCKET_PATH}...")
        reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
        
        print(f"Sending request: {request_payload}")
        writer.write(json.dumps(request_payload).encode('utf-8'))
        await writer.drain()

        response_data = await reader.read(16384)
        
        print("\n--- RESPONSE ---")
        response_json = json.loads(response_data.decode('utf-8'))
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        print("----------------")
        if response_json['status'] == 'success':
            print(f"Successfully received {len(response_json['data'])} events.")
        
        writer.close()
        await writer.wait_closed()

    except FileNotFoundError:
        print(f"Error: Socket file not found at {SOCKET_PATH}. Is the main application running?", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())