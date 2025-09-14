import asyncio
import json
from typing import Any, Optional, TypedDict

MCP_HOST = "127.0.0.1"
MCP_PORT = 8484

_CHUNK_SIZE = 64 * 1024            # 64 KiB
_MAX_MESSAGE_BYTES = 32 * 1024**2  # 32 MiB
_READ_TIMEOUT_SEC = 60.0

class RpcEnvelope(TypedDict, total=False):
    ok: bool
    result: Any
    error: dict

async def _read_json_line(reader: asyncio.StreamReader) -> Optional[dict]:
    buf = bytearray()
    while True:
        try:
            chunk = await asyncio.wait_for(reader.read(_CHUNK_SIZE), timeout=_READ_TIMEOUT_SEC)
        except asyncio.TimeoutError:
            return None
        if not chunk:
            break
        buf += chunk
        if len(buf) > _MAX_MESSAGE_BYTES:
            return None
        if b"\n" in chunk:
            nl = buf.find(b"\n")
            buf = buf[:nl]
            break
    if not buf:
        return None
    try:
        return json.loads(buf.decode("utf-8"))
    except Exception:
        return None

async def call_mcp_ex(method: str, **params: Any) -> RpcEnvelope:
    try:
        reader, writer = await asyncio.open_connection(MCP_HOST, MCP_PORT)

        request = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        writer.write((json.dumps(request) + "\n").encode("utf-8"))
        await writer.drain()

        resp = await _read_json_line(reader)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

        if not resp:
            return {"ok": False, "error": {"message": "empty response", "fatal": False}}

        if resp.get("error"):
            err = resp["error"]
            return {
                "ok": False,
                "error": {
                    "message": err.get("message", "Unknown error"),
                    "code": err.get("code"),
                    "fatal": False,
                },
            }

        result = resp.get("result")
        if result is None:
            return {"ok": False, "error": {"message": "missing result", "fatal": False}}

        return {"ok": True, "result": result}

    except Exception:
        return {"ok": False, "error": {"message": "could not connect to the main control program", "fatal": True}}

async def notify_mcp(method: str, **params: Any) -> None:
    env = await call_mcp_ex(method, **params)
