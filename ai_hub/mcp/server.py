from __future__ import annotations
import sys
import json
import traceback
import asyncio
from .wiring import get_tool_functions
from src.app import App

async def handle_request(app: App, tools: dict, request_line: str) -> dict:
    try:
        req = json.loads(request_line)
        method = req.get("method")
        params = req.get("params", {}) or {}

        if method not in tools:
            return {"error": f"unknown method '{method}'"}
        
        tool_func = tools[method]
        
        result = await tool_func(app, **params)
        return {"result": result}
        
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()[:2000]}

async def main():
    app = App()
    tools = get_tool_functions()
    
    reader = await asyncio.open_connection(stdin=sys.stdin, stdout=None)
    reader = reader[0]

    try:
        while not reader.at_eof():
            line_bytes = await reader.readline()
            line = line_bytes.decode('utf-8').strip()
            if not line:
                continue

            out = await handle_request(app, tools, line)
            
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    finally:
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())