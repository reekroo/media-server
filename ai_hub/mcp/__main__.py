import asyncio
import json
import os
from typing import Any, Dict

from core.settings import Settings
from core.logging import setup_logger, LOG_FILE_PATH
from ai_assistent.composition import create_digest_service
from functions.channels.factory import ChannelFactory
from mcp.dispatcher import Dispatcher
from mcp.context import AppContext
from mcp.registration import discover_and_register_methods

log = setup_logger(__name__, LOG_FILE_PATH)

JSONRPC_VERSION = "2.0"
JSONRPC_INTERNAL_ERROR_CODE = -32603

def _build_error_response(request_id: Any, error: Exception) -> Dict[str, Any]:
    log.error(f"Error processing request (id: {request_id}): {error}", exc_info=True)
    return {
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "error": {"code": JSONRPC_INTERNAL_ERROR_CODE, "message": str(error)}
    }

def _build_success_response(request_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}

async def process_request(request_str: str, dispatcher: Dispatcher) -> Dict[str, Any]:
    request_id = None
    try:
        request = json.loads(request_str)
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        if not method:
            raise ValueError("'method' is a required field")
        
        result = await dispatcher.run(name=method, **params)
        return _build_success_response(request_id, result)

    except Exception as e:
        return _build_error_response(request_id, e)

async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, dispatcher: Dispatcher) -> None:
    peer = writer.get_extra_info('peername')
    log.info(f"Accepted connection from {peer}")
    
    try:
        while True:
            line = await reader.readline()
            if not line:
                log.info(f"Client {peer} disconnected gracefully.")
                break

            request_str = line.decode('utf-8').strip()
            if not request_str:
                continue
            
            log.debug(f"Received from {peer}: {request_str}")
            
            response_data = await process_request(request_str, dispatcher)
            
            response_bytes = (json.dumps(response_data, ensure_ascii=False) + '\n').encode('utf-8')
            writer.write(response_bytes)
            await writer.drain()

    except ConnectionResetError:
        log.warning(f"Connection from {peer} was reset.")
    except Exception as e:
        log.error(f"Unexpected connection error with client {peer}: {e}", exc_info=True)
    finally:
        log.info(f"Closing connection from {peer}")
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

async def main():    
    settings = Settings()
    ai_service = create_digest_service(settings)
    channel_factory = ChannelFactory(settings=settings)
    dispatcher = Dispatcher()
    
    app_context = AppContext(
        settings=settings, ai_service=ai_service,
        channel_factory=channel_factory, dispatcher=dispatcher
    )
    dispatcher.set_app(app_context)
    discover_and_register_methods(dispatcher)
    
    bound_handler = lambda r, w: handle_connection(r, w, dispatcher=dispatcher)

    server = await asyncio.start_server(
        bound_handler,
        host=settings.MCP_HOST,
        port=settings.MCP_PORT
    )

    addr = server.sockets[0].getsockname()
    log.info(f"✅ MCP server started on {addr}. Methods: {list(dispatcher._jobs.keys())}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n gracefully shutdown.")