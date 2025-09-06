from __future__ import annotations
import sys, json, traceback
from .wiring import get_tools

def main():
    tools = get_tools()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {}) or {}
            if method not in tools:
                out = {"error": f"unknown method '{method}'"}
            else:
                result = tools[method](**params)  # tools are sync wrappers
                out = {"result": result}
        except Exception as e:
            out = {"error": str(e), "trace": traceback.format_exc()[:2000]}
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
