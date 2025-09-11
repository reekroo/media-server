import pkgutil
import inspect
from pathlib import Path
from importlib import import_module

from .dispatcher import Dispatcher

def discover_and_register_methods(dispatcher: Dispatcher) -> None:
    """Сканирует директорию rpc_methods/ и регистрирует все публичные функции."""
    print("Discovering RPC methods...")
    methods_dir = Path(__file__).parent / "rpc_methods"
    
    for module_info in pkgutil.iter_modules([str(methods_dir)]):
        module_name = module_info.name
        module = import_module(f"mcp.rpc_methods.{module_name}")
        
        for func_name, func_obj in inspect.getmembers(module, inspect.isfunction):
            if not func_name.startswith("_"):
                # Преобразуем имя файла и функции в имя RPC-метода
                # Например, файл news.py, функция build_digest -> "news.build"
                rpc_method_name = f"{module_name}.{func_name.replace('_digest','').replace('_brief','')}"
                dispatcher.register(rpc_method_name, func_obj)
                print(f"  -> Registered RPC method '{rpc_method_name}'")