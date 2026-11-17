import os
import uuid
import datetime
from backend.config import Config

class SupabaseService:
    """
    Supabase Database & Storage Gateway
    Supports both real Supabase PostgreSQL/Storage and resilient local fallback.
    """
    def __init__(self):
        self._client = None
        self._is_configured = False
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
        
        if url and key and not "placeholder" in url and not "placeholder" in key:
            try:
                from supabase import create_client
                self._client = create_client(url, key)
                self._is_configured = True
                print("[SupabaseService] Connected to Supabase:", url)
            except Exception as e:
                print(f"[SupabaseService] Failed to initialize Supabase client: {e}")
                self._is_configured = False
        else:
            print("[SupabaseService] Running with local mock fallback (no credentials configured)")

    @property
    def client(self):
        self._ensure_init()
        return self._client

    @property
    def is_configured(self):
        self._ensure_init()
        return self._is_configured

    # --------------------------------------------------------------------------
    # Auth helpers
    # --------------------------------------------------------------------------
    def verify_token(self, token: str):
        """Verify Supabase JWT token and return user payload"""
        if not token:
            return None
        if self.is_configured and self.client:
            try:
                user_res = self.client.auth.get_user(token)
                if user_res and user_res.user:
                    return {
                        "id": user_res.user.id,
                        "email": user_res.user.email,
                        "user_metadata": user_res.user.user_metadata or {}
                    }
            except Exception as e:
                print(f"[SupabaseService] Token verification error: {e}")
                return None
        
        # Local mock token validation for testing/dev
        if token.startswith("mock-") or token.startswith("agri-"):
            return {
                "id": "mock-farmer-uuid-001",
                "email": "farmer@agrisense.org",
                "user_metadata": {"first_name": "Ramesh", "farmer_experience_level": "Beginner"}
            }
        return None

    # --------------------------------------------------------------------------
    # Profiles
    # --------------------------------------------------------------------------
    def get_profile(self, user_id: str):
        if self.is_configured and self.client:
            try:
                res = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] get_profile error: {e}")
        return {
            "id": user_id,
            "first_name": "Ramesh",
            "last_name": "Patil",
            "farmer_experience_level": "Beginner",
            "preferred_language": "en"
        }

    # --------------------------------------------------------------------------
    # Crop Recommendations
    # --------------------------------------------------------------------------
    def save_crop_recommendation(self, user_id, input_params, recommendations, model_name="RandomForestClassifier"):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "input_parameters": input_params,
            "recommended_crops": recommendations,
            "model_name": model_name,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                self.client.table("crop_recommendations").insert(record).execute()
            except Exception as e:
                print(f"[SupabaseService] save_crop_recommendation error: {e}")
        return record

    # --------------------------------------------------------------------------
    # Disease Detection History
    # --------------------------------------------------------------------------
    def save_disease_prediction(self, user_id, crop_id, image_url, disease_name, confidence, severity, treatment, organic):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "crop_id": crop_id,
            "image_url": image_url,
            "disease_name": disease_name,
            "confidence": float(confidence),
            "severity": severity,
            "treatment_advice": treatment,
            "organic_treatment": organic,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                self.client.table("disease_predictions").insert(record).execute()
            except Exception as e:
                print(f"[SupabaseService] save_disease_prediction error: {e}")
        return record

    def get_disease_history(self, user_id=None, limit=20):
        if self.is_configured and self.client and user_id:
            try:
                res = self.client.table("disease_predictions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] get_disease_history error: {e}")
        return []

    # --------------------------------------------------------------------------
    # Price Predictions
    # --------------------------------------------------------------------------
    def save_price_prediction(self, user_id, crop_name, market, current_price, forecast_data, best_date, best_price, model_name="GradientBoosting"):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "crop_name": crop_name,
            "market": market,
            "current_price": float(current_price),
            "forecast_data": forecast_data,
            "best_selling_date": best_date,
            "best_selling_price": float(best_price),
            "model_name": model_name,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                self.client.table("price_predictions").insert(record).execute()
            except Exception as e:
                print(f"[SupabaseService] save_price_prediction error: {e}")
        return record

    # --------------------------------------------------------------------------
    # Crop Management & Monitoring
    # --------------------------------------------------------------------------
    def add_crop(self, user_id, data):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "farm_id": data.get("farm_id"),
            "crop_name": data.get("crop_name"),
            "crop_variety": data.get("crop_variety", "Standard"),
            "sowing_date": data.get("sowing_date"),
            "expected_harvest_date": data.get("expected_harvest_date"),
            "season": data.get("season", "Kharif"),
            "current_growth_stage": data.get("current_growth_stage", "Sowing"),
            "status": "Active",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                res = self.client.table("crops").insert(record).execute()
                return res.data[0] if res.data else record
            except Exception as e:
                print(f"[SupabaseService] add_crop error: {e}")
        return record

    def get_user_crops(self, user_id):
        if self.is_configured and self.client:
            try:
                res = self.client.table("crops").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] get_user_crops error: {e}")
        return []

    def add_crop_monitoring(self, user_id, data):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "crop_id": data.get("crop_id"),
            "observation_date": data.get("observation_date", datetime.date.today().isoformat()),
            "growth_stage": data.get("growth_stage", "Vegetative"),
            "health_status": data.get("health_status", "Healthy"),
            "notes": data.get("notes", ""),
            "image_url": data.get("image_url", ""),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                res = self.client.table("crop_monitoring").insert(record).execute()
                return res.data[0] if res.data else record
            except Exception as e:
                print(f"[SupabaseService] add_crop_monitoring error: {e}")
        return record

    # --------------------------------------------------------------------------
    # Calendar Tasks
    # --------------------------------------------------------------------------
    def save_calendar_tasks(self, tasks: list):
        if not tasks:
            return []
        if self.is_configured and self.client:
            try:
                res = self.client.table("crop_calendar_tasks").insert(tasks).execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] save_calendar_tasks error: {e}")
        return tasks

    def get_calendar_tasks(self, user_id=None, crop_id=None):
        if self.is_configured and self.client:
            try:
                query = self.client.table("crop_calendar_tasks").select("*")
                if user_id:
                    query = query.eq("user_id", user_id)
                if crop_id:
                    query = query.eq("crop_id", crop_id)
                res = query.order("task_date").execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] get_calendar_tasks error: {e}")
        return []

    def update_calendar_task(self, task_id: str, updates: dict):
        if self.is_configured and self.client:
            try:
                res = self.client.table("crop_calendar_tasks").update(updates).eq("id", task_id).execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] update_calendar_task error: {e}")
        return [updates]

    # --------------------------------------------------------------------------
    # Chatbot History
    # --------------------------------------------------------------------------
    def save_chat_message(self, user_id, message, reply, language="en"):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_message": message,
            "bot_response": reply,
            "language": language,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                self.client.table("chatbot_history").insert(record).execute()
            except Exception as e:
                print(f"[SupabaseService] save_chat_message error: {e}")
        return record

    # --------------------------------------------------------------------------
    # Direct Market Requests
    # --------------------------------------------------------------------------
    def save_deal_request(self, deal_data):
        record = {
            "id": str(uuid.uuid4()),
            "user_id": deal_data.get("user_id"),
            "company_name": deal_data.get("company_name", deal_data.get("company", "Company")),
            "farmer_name": deal_data.get("farmer_name", deal_data.get("name", "Farmer")),
            "phone": deal_data.get("phone", ""),
            "location": deal_data.get("location", ""),
            "crop_name": deal_data.get("crop_name", deal_data.get("crop", "Produce")),
            "crop_variety": deal_data.get("crop_variety", ""),
            "quantity": float(deal_data.get("quantity", deal_data.get("qty", 10))),
            "expected_price": float(deal_data.get("expected_price", deal_data.get("price", 2000))),
            "message": deal_data.get("message", ""),
            "status": "Pending",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.is_configured and self.client:
            try:
                res = self.client.table("market_deal_requests").insert(record).execute()
                return res.data[0] if res.data else record
            except Exception as e:
                print(f"[SupabaseService] save_deal_request error: {e}")
        return record

    def get_deal_requests(self, user_id=None):
        if self.is_configured and self.client:
            try:
                query = self.client.table("market_deal_requests").select("*")
                if user_id:
                    query = query.eq("user_id", user_id)
                res = query.order("created_at", desc=True).execute()
                return res.data
            except Exception as e:
                print(f"[SupabaseService] get_deal_requests error: {e}")
        return []

    # --------------------------------------------------------------------------
    # Government Schemes
    # --------------------------------------------------------------------------
    def get_government_schemes(self):
        if self.is_configured and self.client:
            try:
                res = self.client.table("government_schemes").select("*").execute()
                if res.data and len(res.data) > 0:
                    return res.data
            except Exception as e:
                print(f"[SupabaseService] get_government_schemes error: {e}")
                
        # High quality default Indian government schemes
        return [
            {
                "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                "category": "Income Support",
                "benefit": "₹6,000 per year directly into bank accounts in 3 equal installments of ₹2,000.",
                "eligibility": "All landholding farmer families across India.",
                "apply": "pmkisan.gov.in"
            },
            {
                "name": "PM Fasal Bima Yojana (PMFBY)",
                "category": "Crop Insurance",
                "benefit": "Comprehensive crop insurance against natural calamities at minimal farmer premium (1.5%–5%).",
                "eligibility": "All farmers growing notified food, oilseeds and commercial crops.",
                "apply": "pmfby.gov.in"
            },
            {
                "name": "Kisan Credit Card (KCC)",
                "category": "Agricultural Credit",
                "benefit": "Affordable agricultural credit up to ₹3 Lakh at an effective interest rate of 4% p.a.",
                "eligibility": "Small, marginal, and tenant farmers, oral lessees and SHGs.",
                "apply": "myscheme.gov.in"
            },
            {
                "name": "Soil Health Card Scheme",
                "category": "Soil Health",
                "benefit": "Free customized nutrient & fertilizer recommendation report for 12 essential nutrients.",
                "eligibility": "All farmers with agricultural land across all Indian states.",
                "apply": "soilhealth.dac.gov.in"
            },
            {
                "name": "PM Krishi Sinchayee Yojana (PMKSY)",
                "category": "Irrigation",
                "benefit": "Up to 55% government subsidy on drip and sprinkler micro-irrigation systems.",
                "eligibility": "Farmers with cultivable land and an accessible water source.",
                "apply": "pmksy.gov.in"
            }
        ]

# Global singleton
supabase_service = SupabaseService()
