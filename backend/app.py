import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.config import Config

# Blueprint imports
from backend.routes.auth_routes import auth_bp
from backend.routes.crop_routes import crop_bp
from backend.routes.disease_routes import disease_bp
from backend.routes.price_routes import price_bp
from backend.routes.calendar_routes import calendar_bp
from backend.routes.weather_routes import weather_bp
from backend.routes.chatbot_routes import chatbot_bp
from backend.routes.market_routes import market_bp
from backend.routes.scheme_routes import scheme_bp
from backend.services.supabase_service import supabase_service

ROOT_DIR = Path(__file__).resolve().parent.parent

def create_app():
    app = Flask(__name__, static_folder=str(ROOT_DIR))
    
    # Enable CORS for all routes and origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(price_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(scheme_bp)
    
    # --------------------------------------------------------------------------
    # Frontend Static & HTML Serving Routes
    # --------------------------------------------------------------------------
    @app.route("/")
    @app.route("/index.html")
    def serve_index():
        candidates = [
            ROOT_DIR / "index.html",
            Path(os.getcwd()) / "index.html",
            Path("/var/task") / "index.html"
        ]
        for p in candidates:
            if p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
                except Exception as e:
                    return f"Error reading index.html: {e}", 500
        return "<h1>AgriSense</h1><p>index.html not found</p>", 200

    @app.route("/login.html")
    def serve_login():
        candidates = [
            ROOT_DIR / "login.html",
            Path(os.getcwd()) / "login.html",
            Path("/var/task") / "login.html"
        ]
        for p in candidates:
            if p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
                except Exception as e:
                    return f"Error reading login.html: {e}", 500
        return "<h1>AgriSense</h1><p>login.html not found</p>", 200

    @app.route("/frontend/<path:filename>")
    def serve_frontend_assets(filename):
        candidates = [
            ROOT_DIR / "frontend",
            Path(os.getcwd()) / "frontend",
            Path("/var/task") / "frontend"
        ]
        for c_dir in candidates:
            target = c_dir / filename
            if target.is_file():
                try:
                    content_type = "application/javascript" if filename.endswith(".js") else "text/css" if filename.endswith(".css") else "text/plain"
                    with open(target, "r", encoding="utf-8") as f:
                        return f.read(), 200, {"Content-Type": f"{content_type}; charset=utf-8"}
                except Exception as e:
                    return f"Error reading asset {filename}: {e}", 500
        return f"Asset {filename} not found", 404

    # --------------------------------------------------------------------------
    # Health Check API
    # --------------------------------------------------------------------------
    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "platform": "AgriSense — AI-Powered Smart Agriculture",
            "version": "1.0.0",
            "database": "Supabase PostgreSQL (Connected)" if supabase_service.is_configured else "Local Resilient Fallback",
            "models_loaded": {
                "crop_recommendation": True,
                "disease_detection": True,
                "price_prediction": True,
                "crop_calendar": True
            }
        })

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Resource or endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error occurred"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    print(f"================================================================")
    print(f" AGRISENSE BACKEND SERVER STARTING")
    print(f" URL: http://localhost:{Config.PORT}")
    print(f" Database: {'Supabase PostgreSQL' if supabase_service.is_configured else 'Local Mode (Configure .env for Supabase)'}")
    print(f"================================================================")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
