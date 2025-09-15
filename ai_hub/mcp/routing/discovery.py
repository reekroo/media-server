from __future__ import annotations
import importlib
import pkgutil
from typing import List

from mcp.tools.base import ToolSpec

def list_tools() -> List[ToolSpec]:
    tools: List[ToolSpec] = []

    package_name = "mcp.tools"
    package = importlib.import_module(package_name)

    for finder, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if ispkg or modname in {"base", "__init__"}:
            continue
        module = importlib.import_module(f"{package_name}.{modname}")
        spec = getattr(module, "TOOL", None)
        if isinstance(spec, ToolSpec):
            tools.append(spec)

    return tools
