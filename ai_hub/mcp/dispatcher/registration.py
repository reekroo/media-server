import pkgutil
import inspect
from pathlib import Path
from importlib import import_module

from .dispatcher import Dispatcher

def discover_and_register_methods(dispatcher: Dispatcher) -> None:
    print("✅ Discovering RPC methods (recursive)...")
    
    mcp_root = Path(__file__).parent.parent
    
    packages_to_scan = [
        (mcp_root / "rpc_methods", "mcp.rpc_methods."),
        (mcp_root / "runner", "mcp.runner.")
    ]

    for path, prefix in packages_to_scan:
        for module_finder, module_name, is_pkg in pkgutil.walk_packages(path=[str(path)], prefix=prefix):
            if is_pkg:
                continue
            
            try:
                module = import_module(module_name) 
            except ImportError as e:
                print(f"⚠️ Could not import module '{module_name}': {e}")
                continue

            for func_name, func_obj in inspect.getmembers(module, inspect.iscoroutinefunction):
                if inspect.getmodule(func_obj) is not module or func_name.startswith("_"):
                    continue
                
                relative_name = module_name.replace(prefix, "") 
                base_name = relative_name.split('.')[0] 
                rpc_method_name = f"{base_name}.{func_name}"

                dispatcher.register(rpc_method_name, func_obj)
                print(f"☑️ Registered RPC method '{rpc_method_name}' from module '{module_name}'")