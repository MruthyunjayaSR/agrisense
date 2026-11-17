from flask import Blueprint, request
from backend.models.disease_detection import disease_model
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth
from backend.utils.helpers import success_response, error_response

disease_bp = Blueprint("disease_bp", __name__)

@disease_bp.route("/api/disease/detect", methods=["POST"])
@optional_auth
def detect_disease():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image")
    
    # Also support multipart file uploads
    if not image_data and "file" in request.files:
        image_data = request.files["file"].read()
        
    if not image_data:
        return error_response("Leaf image data (Base64 or file upload) is required", status_code=400)
        
    result = disease_model.predict_from_image(image_data)
    
    # Save to Supabase prediction history
    user_id = request.user["id"] if getattr(request, "user", None) else None
    crop_id = data.get("crop_id")
    supabase_service.save_disease_prediction(
        user_id=user_id,
        crop_id=crop_id,
        image_url=None, # Could be uploaded to Supabase Storage if configured
        disease_name=result["disease"],
        confidence=result["confidence"],
        severity=result["severity"],
        treatment=result["treatment"],
        organic=result["organic_treatment"]
    )
    
    # Return formatted result matching frontend index.html expectations directly
    return success_response(**result)


@disease_bp.route("/api/disease/list", methods=["GET"])
def list_diseases():
    """
    Returns disease reference library for frontend catalog
    """
    diseases = disease_model.get_supported_diseases()
    return success_response(diseases=diseases)


@disease_bp.route("/api/disease/history", methods=["GET"])
@optional_auth
def disease_history():
    user_id = request.user["id"] if getattr(request, "user", None) else None
    history = supabase_service.get_disease_history(user_id)
    return success_response(history=history)
