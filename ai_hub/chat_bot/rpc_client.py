import asyncio
import json
from typing import Any

MCP_HOST = "127.0.0.1"
MCP_PORT = 8484

async def call_mcp(method: str, **params: Any) -> Any:
    try:
        reader, writer = await asyncio.open_connection(MCP_HOST, MCP_PORT)

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        
        writer.write((json.dumps(request) + '\n').encode())
        await writer.drain()

        response_raw = await reader.readline()
        response = json.loads(response_raw.decode())

        writer.close()
        await writer.wait_closed()

        if response.get("error"):
            return f"MCP Error: {response['error'].get('message', 'Unknown error')}"

        return response.get("result", "No result from MCP.")

    except Exception as e:
        print(f"Error calling MCP method '{method}': {e}")
        return f"Fatal Error: Could not connect to the main control program."