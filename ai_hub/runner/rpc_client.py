import asyncio
import json
import logging
from typing import Any, Dict

from core.settings import Settings

log = logging.getLogger(__name__)

_READ_TIMEOUT_SEC = 60.0
_JSON_RPC_VERSION = "2.0"

class RpcClient:
    def __init__(self, settings: Settings):
        self._host = settings.MCP_HOST
        self._port = settings.MCP_PORT
        log.info(f"RpcClient configured to connect to MCP at {self._host}:{self._port}")

    async def _read_json_response(self, reader: asyncio.StreamReader) -> Dict[str, Any] | None:
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=_READ_TIMEOUT_SEC)
            if not line:
                return None
            return json.loads(line)
        except asyncio.TimeoutError:
            log.error("Timeout while reading response from MCP.")
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.error(f"Failed to decode JSON response from MCP: {e}")
            return None

    async def call(self, method: str, **params: Any) -> Dict[str, Any]:
        try:
            reader, writer = await asyncio.open_connection(self._host, self._port)
        except Exception as e:
            log.error(f"Could not connect to MCP at {self._host}:{self._port}. Error: {e}")
            return {"ok": False, "error": {"message": "connection failed", "fatal": True}}

        response: Dict[str, Any] = {}
        try:
            request = {
                "jsonrpc": _JSON_RPC_VERSION, "method": method,
                "params": params, "id": 1
            }
            writer.write((json.dumps(request) + "\n").encode("utf-8"))
            await writer.drain()

            raw_resp = await self._read_json_response(reader)

            if not raw_resp:
                response = {"ok": False, "error": {"message": "empty or invalid response"}}
            elif "error" in raw_resp:
                response = {"ok": False, "error": raw_resp["error"]}
            elif "result" not in raw_resp:
                response = {"ok": False, "error": {"message": "missing 'result' in response"}}
            else:
                response = {"ok": True, "result": raw_resp["result"]}
        
        except Exception as e:
            log.error(f"An unexpected error occurred during RPC call '{method}': {e}", exc_info=True)
            response = {"ok": False, "error": {"message": "unexpected client error"}}
        
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
        
        return response