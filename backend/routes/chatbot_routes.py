from flask import Blueprint, request
from backend.services.chatbot_service import chatbot_service
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth
from backend.utils.helpers import success_response, error_response

chatbot_bp = Blueprint("chatbot_bp", __name__)

@chatbot_bp.route("/api/chatbot", methods=["POST"])
@optional_auth
def chat_with_agribot():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    language = data.get("language", "en")
    language_name = data.get("language_name", "English")
    
    if not message:
        return error_response("Message cannot be empty", status_code=400)
        
    user_id = request.user["id"] if getattr(request, "user", None) else None
    farmer_level = "Beginner"
    if user_id:
        profile = supabase_service.get_profile(user_id)
        if profile:
            farmer_level = profile.get("farmer_experience_level", "Beginner")
            
    reply = chatbot_service.respond(
        message=message,
        language=language,
        language_name=language_name,
        farmer_level=farmer_level
    )
    
    # Store in chatbot_history table in Supabase
    supabase_service.save_chat_message(
        user_id=user_id,
        message=message,
        reply=reply,
        language=language
    )
    
    # Frontend index.html lines 1601 & 1215 expects { reply: "..." }
    return success_response(reply=reply, language=language)


@chatbot_bp.route("/api/chatbot/history", methods=["GET"])
@optional_auth
def get_chat_history():
    user_id = request.user["id"] if getattr(request, "user", None) else None
    if not user_id:
        return success_response(history=[])
        
    if supabase_service.is_configured and supabase_service.client:
        try:
            res = supabase_service.client.table("chatbot_history").select("*").eq("user_id", user_id).order("created_at", desc=False).limit(30).execute()
            return success_response(history=res.data)
        except Exception as e:
            print(f"[Chatbot] History error: {e}")
            
    return success_response(history=[])
