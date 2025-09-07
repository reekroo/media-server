from __future__ import annotations
import sys
import json
import traceback
import asyncio
import logging
import os

from .wiring import get_tool_functions
from src.container import build_services, Services

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')

async def handle_request(services: Services, tools: dict, request_line: str) -> dict:
    try:
        req = json.loads(request_line)
        method = req.get("method")
        params = req.get("params", {}) or {}

        if method not in tools:
            return {"error": f"unknown method '{method}'"}
        
        tool_func = tools[method]
        
        result = await tool_func(services, **params)
        return {"result": result}
        
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()[:2000]}

async def main():
    services = build_services()
    tools = get_tool_functions()
    loop = asyncio.get_running_loop()
    
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    transport, protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(transport, protocol, None, loop)

    try:
        line_bytes = await reader.readline()
        line = line_bytes.decode('utf-8').strip()

        if line:
            out = await handle_request(services, tools, line)
            
            try:
                writer.write(json.dumps(out, ensure_ascii=False).encode('utf-8') + b'\n')
                await writer.drain()
            except (BrokenPipeError, ConnectionResetError):
                logging.info("Client disconnected before response could be sent. (Broken Pipe)")
        
    finally:
        if writer:
            writer.close()
        await services.http_session.close()

if __name__ == "__main__":
    asyncio.run(main())