import asyncio
import pkgutil
import inspect
from pathlib import Path
from importlib import import_module
from jsonrpc_async import Server

# Главные компоненты системы
from core.settings import Settings
from core.logging import setup_logger
from ai_assistent.agents.factory import agent_factory
from ai_assistent.service import DigestService
from functions.channels.factory import ChannelFactory

from .dispatcher import Dispatcher
from .context import AppContext

def _discover_and_register_methods(dispatcher: Dispatcher) -> None:
    """Сканирует директорию rpc_methods/ и регистрирует все публичные функции."""
    print("Discovering RPC methods...")
    methods_dir = Path(__file__).parent / "rpc_methods"
    
    for module_info in pkgutil.iter_modules([str(methods_dir)]):
        module_name = module_info.name
        module = import_module(f".rpc_methods.{module_name}", package="mcp")
        
        for func_name, func_obj in inspect.getmembers(module, inspect.isfunction):
            if not func_name.startswith("_"):
                rpc_method_name = f"{module_name}.{func_name.replace('_digest','').replace('_brief','')}"
                dispatcher.register(rpc_method_name, func_obj)
                print(f"  -> Registered RPC method '{rpc_method_name}'")

async def main():
    # 1. Инициализация базовых компонентов
    settings = Settings()
    setup_logger(settings.STATE_DIR)
    
    # 2. Инициализация "мозга" (ai_assistent)
    llm_agent = agent_factory(settings)
    ai_service = DigestService(agent=llm_agent)

    # 3. Инициализация "рук" (functions)
    channel_factory = ChannelFactory()

    # 4. Создание общего контекста приложения
    app_context = AppContext(
        settings=settings,
        ai_service=ai_service,
        channel_factory=channel_factory
    )

    # 5. Настройка диспетчера MCP
    dispatcher = Dispatcher(app=app_context)
    _discover_and_register_methods(dispatcher)
    
    # 6. Запуск TCP-сервера для приема JSON-RPC вызовов
    server = Server(dispatcher.run)
    await server.start(host="127.0.0.1", port=8484)
    print(f"✅ MCP server started on tcp://127.0.0.1:8484")
    
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        print("MCP server shutting down.")
    finally:
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP server stopped by user.")