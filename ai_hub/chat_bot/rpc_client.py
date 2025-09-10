import jsonrpc_async
from typing import Any, Dict

MCP_HOST = "127.0.0.1"
MCP_PORT = 8484

async def call_mcp(method: str, **params: Any) -> Any:
    """Подключается к MCP и вызывает RPC-метод."""
    try:
        client = jsonrpc_async.Client(f"tcp://{MCP_HOST}:{MCP_PORT}")
        return await client.call(method, **params)
    except Exception as e:
        print(f"Error calling MCP method '{method}': {e}")
        return f"Error: Could not connect to the main control program."