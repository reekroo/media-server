import pkgutil
import inspect
from pathlib import Path
from importlib import import_module

from .dispatcher import Dispatcher

def discover_and_register_methods(dispatcher: Dispatcher) -> None:
    print("✅ Discovering RPC methods (recursive)...")
    methods_pkg_path = Path(__file__).parent / "rpc_methods"
    methods_prefix = "mcp.rpc_methods."
    
    for module_finder, module_name, is_pkg in pkgutil.walk_packages(
        path=[str(methods_pkg_path)], 
        prefix=methods_prefix
    ):
        if is_pkg:
            continue

        try:
            module = import_module(module_name)
        except ImportError as e:
            print(f"⚠️ Could not import module '{module_name}': {e}")
            continue

        for func_name, func_obj in inspect.getmembers(module, inspect.iscoroutinefunction):
            if inspect.getmodule(func_obj) is not module:
                continue
            if func_name.startswith("_"):
                continue

            relative_module_path = module.__name__.replace(methods_prefix, "")
            base_name = relative_module_path.split('.')[0]
            
            short_func_name = func_name.replace('_digest','').replace('_brief','')
            rpc_method_name = f"{base_name}.{short_func_name}"

            dispatcher.register(rpc_method_name, func_obj)
            print(f"☑️ Registered RPC method '{rpc_method_name}' from module '{module_name}'")