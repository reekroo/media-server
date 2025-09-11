import asyncio
import json
import logging
import os
from typing import Any

from core.settings import Settings
from core.logging import setup_logger
from ai_assistent.agents.factory import agent_factory
from ai_assistent.service import DigestService
from functions.channels.factory import ChannelFactory
from mcp.dispatcher import Dispatcher
from mcp.context import AppContext
from mcp.registration import discover_and_register_methods

log = logging.getLogger("MCP")

# --- ИСПРАВЛЕНИЕ №1: Обработчик теперь принимает dispatcher как аргумент ---
async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, dispatcher: Dispatcher) -> None:
    """Обрабатывает одно клиентское подключение."""
    peer = writer.get_extra_info('peername')
    log.info(f"Accepted connection from {peer}")
    
    try:
        while True:
            line = await reader.readline()
            if not line:
                break

            request_str = line.decode('utf-8').strip()
            log.debug(f"Received from {peer}: {request_str}")

            response: dict[str, Any]
            try:
                request = json.loads(request_str)
                method = request.get("method")
                params = request.get("params", {})
                
                if not method:
                    raise ValueError("'method' is a required field")

                # Используем dispatcher, который был передан в функцию
                result = await dispatcher.run(name=method, **params)
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}

            except Exception as e:
                log.error(f"Error processing request from {peer}: {e}", exc_info=True)
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            
            response_bytes = (json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8')
            writer.write(response_bytes)
            await writer.drain()

    except ConnectionResetError:
        log.info(f"Connection from {peer} reset.")
    except Exception as e:
        log.error(f"Unexpected error with client {peer}: {e}", exc_info=True)
    finally:
        log.info(f"Closing connection from {peer}")
        writer.close()
        await writer.wait_closed()

async def main():
    env_file = ".env"
    if not os.path.exists(env_file):
        env_file = "/etc/default/ai-hub"
        print(f"Local .env not found, using system-wide config: {env_file}")

    settings = Settings(_env_file=env_file)
    setup_logger(settings.STATE_DIR)
    
    llm_agent = agent_factory(settings)
    ai_service = DigestService(agent=llm_agent)
    channel_factory = ChannelFactory(settings=settings)
    
    app_context = AppContext(
        settings=settings,
        ai_service=ai_service,
        channel_factory=channel_factory
    )
    
    dispatcher = Dispatcher(app=app_context)
    discover_and_register_methods(dispatcher)
    
    # --- ИСПРАВЛЕНИЕ №2: Создаем "обертку" для нашего обработчика ---
    # Это позволяет "запомнить" dispatcher для всех будущих вызовов
    connection_handler = lambda r, w: handle_connection(r, w, dispatcher=dispatcher)

    # --- ИСПРАВЛЕНИЕ №3: Вызываем start_server с правильными аргументами ---
    server = await asyncio.start_server(
        connection_handler, # <-- Передаем новую обертку
        host="127.0.0.1", 
        port=8484,
    )

    addr = server.sockets[0].getsockname()
    log.info(f"✅ MCP server started on {addr}. Methods: {list(dispatcher._jobs.keys())}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP server stopped by user.")