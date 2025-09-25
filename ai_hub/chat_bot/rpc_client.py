import asyncio
import json
import logging
from typing import Any, TypedDict

from core.settings import Settings
from core.serialization import maybe_unjson_string

log = logging.getLogger(__name__)

class RpcEnvelope(TypedDict, total=False):
    ok: bool
    result: Any
    error: dict

class ChatRpcClient:
    _READ_TIMEOUT_SEC = 60.0
    _JSON_RPC_VERSION = "2.0"
    _BUFFER_LIMIT_BYTES = 10 * 1024 * 1024 

    def __init__(self, settings: Settings):
        self._host = settings.MCP_HOST
        self._port = settings.MCP_PORT
        log.info(f"RpcClient configured to connect to MCP at {self._host}:{self._port}")

    async def _read_json_response(self, reader: asyncio.StreamReader) -> dict[str, Any] | None:
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=self._READ_TIMEOUT_SEC)
            if not line: return None
            return json.loads(line)
        except asyncio.TimeoutError:
            log.error("Timeout while reading response from MCP.")
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.error(f"Failed to decode JSON response from MCP: {e}")
            return None
        except ValueError as e:
            log.error(f"Buffer limit exceeded while reading response from MCP: {e}")
            return None

    async def call(self, method: str, **params: Any) -> RpcEnvelope:
        try:
            reader, writer = await asyncio.open_connection(
                self._host, self._port, limit=self._BUFFER_LIMIT_BYTES
            )
        except Exception as e:
            log.error(f"Fatal: Could not connect to MCP. Error: {e}")
            return {"ok": False, "error": {"message": "could not connect to MCP", "fatal": True}}

        response: RpcEnvelope = {}
        try:
            request_id = 1
            request = {
                "jsonrpc": self._JSON_RPC_VERSION, "method": method,
                "params": params, "id": request_id
            }
            writer.write((json.dumps(request) + "\n").encode("utf-8"))
            await writer.drain()

            raw_resp = await self._read_json_response(reader)

            if not raw_resp:
                response = {"ok": False, "error": {"message": "empty or invalid response"}}
            elif "error" in raw_resp:
                response = {"ok": False, "error": raw_resp["error"]}
            elif (result := maybe_unjson_string(raw_resp.get("result"))) is not None:
                response = {"ok": True, "result": result}
            else:
                response = {"ok": False, "error": {"message": "missing 'result' in response"}}

        except Exception as e:
            log.error(f"Unexpected client error during '{method}' call.", exc_info=e)
            response = {"ok": False, "error": {"message": "unexpected client error"}}
        
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
        
        return response

UI_PREFIX_ERROR = "🟥 MCP Error: "
UI_PREFIX_FATAL = "🟥 Fatal Error: "

def ui_error_message(error: dict) -> str:
    prefix = UI_PREFIX_FATAL if error.get("fatal") else UI_PREFIX_ERROR
    msg = error.get("message", "unknown error")
    return f"{prefix}{msg}"