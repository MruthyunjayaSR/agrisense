import os
import sys
import traceback

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

init_error = None
try:
    from backend.app import app as flask_app
except BaseException:
    init_error = traceback.format_exc()

class ErrorFallbackApp:
    def __init__(self, error_msg):
        self.error_msg = error_msg

    def __call__(self, environ, start_response):
        status = "200 OK"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*")
        ]
        start_response(status, headers)
        report = (
            "=== AGRISENSE BACKEND STARTUP ERROR REPORT ===\n"
            f"Python Version: {sys.version}\n"
            f"CWD: {os.getcwd()}\n"
            f"Sys Path: {sys.path}\n\n"
            f"Error Details:\n{self.error_msg}\n"
        )
        return [report.encode("utf-8")]

class SafeWsgiWrapper:
    def __init__(self, target_app):
        self.target_app = target_app

    def __call__(self, environ, start_response):
        try:
            return self.target_app(environ, start_response)
        except BaseException:
            err = traceback.format_exc()
            status = "200 OK"
            headers = [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Access-Control-Allow-Origin", "*")
            ]
            start_response(status, headers)
            report = (
                "=== AGRISENSE RUNTIME ERROR IN HANDLER ===\n"
                f"Path: {environ.get('PATH_INFO', '')}\n"
                f"Method: {environ.get('REQUEST_METHOD', '')}\n\n"
                f"Traceback:\n{err}\n"
            )
            return [report.encode("utf-8")]

if init_error:
    app = ErrorFallbackApp(init_error)
else:
    app = SafeWsgiWrapper(flask_app)

if __name__ == "__main__":
    if init_error:
        print("Startup Error:", init_error)
    else:
        flask_app.run(port=5000, debug=True)
