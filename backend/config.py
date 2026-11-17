import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "agrisense-super-secret-key-2025")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qxocrgejzvtgsdzjjewl.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_wexU-OLQifldyWaWutyjCg_q38g-lv-")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "sb_publishable_wexU-OLQifldyWaWutyjCg_q38g-lv-")

    # Storage bucket name for uploaded crop / leaf images
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "crop-images")

    # External APIs
    # Open-Meteo is free and doesn't require an API key by default!
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # AI / LLM API Key (e.g. Gemini API, Groq, or OpenAI)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("AI_API_KEY", ""))
    
    # ML Models path
    SAVED_MODELS_DIR = BASE_DIR / "ml" / "saved_models"
