import os
import sys
import traceback

# Ensure repository root is on sys.path so 'backend' is cleanly importable in Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.app import app
except Exception as e:
    import json
    err_trace = traceback.format_exc()
    print(f"[Vercel Handler] Error importing backend.app: {err_trace}")
    
    def app(environ, start_response):
        body = json.dumps({
            "success": False,
            "error": "Vercel backend initialization error",
            "details": str(e),
            "traceback": err_trace
        }).encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*")
        ]
        start_response(status, headers)
        return [body]
