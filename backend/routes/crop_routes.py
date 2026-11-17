from flask import Blueprint, request
from backend.models.crop_recommendation import crop_model
from backend.models.crop_calendar import crop_calendar
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth, require_auth
from backend.utils.validators import validate_crop_recommendation_input
from backend.utils.helpers import success_response, error_response

crop_bp = Blueprint("crop_bp", __name__)

@crop_bp.route("/api/crops/recommend", methods=["POST"])
@optional_auth
def recommend_crops():
    data = request.get_json(silent=True) or {}
    
    valid, errors = validate_crop_recommendation_input(data)
    if not valid:
        return error_response("Invalid input parameters", errors=errors, status_code=400)
        
    N = float(data.get("N", 80))
    P = float(data.get("P", 50))
    K = float(data.get("K", 60))
    temp = float(data.get("temperature", 26))
    hum = float(data.get("humidity", 65))
    ph = float(data.get("ph", 6.5))
    rain = float(data.get("rainfall", 120))
    season = str(data.get("season", "kharif")).lower()
    
    recommendations = crop_model.predict(
        N=N, P=P, K=K,
        temperature=temp,
        humidity=hum,
        ph=ph,
        rainfall=rain,
        season=season
    )
    
    # Save recommendation to database if user is authenticated
    user_id = request.user["id"] if getattr(request, "user", None) else None
    supabase_service.save_crop_recommendation(user_id, data, recommendations)
    
    # Match frontend index.html expectations exactly:
    # d.season, d.recommendations
    return success_response(
        season=season,
        recommendations=recommendations,
        model_name="RandomForestClassifier"
    )


@crop_bp.route("/api/crops/add", methods=["POST"])
@optional_auth
def add_user_crop():
    data = request.get_json(silent=True) or {}
    crop_name = data.get("crop_name")
    if not crop_name:
        return error_response("Crop name is required", status_code=400)
        
    user_id = request.user["id"] if getattr(request, "user", None) else "guest-farmer"
    saved = supabase_service.add_crop(user_id, data)
    
    # Automatically generate calendar tasks for this crop
    sowing_date = data.get("sowing_date")
    if sowing_date:
        cal = crop_calendar.generate_full_crop_calendar(
            crop_name=crop_name,
            sowing_date_str=sowing_date,
            variety=data.get("crop_variety", "Standard"),
            user_id=user_id,
            farm_id=data.get("farm_id")
        )
        supabase_service.save_calendar_tasks(cal["tasks"])
        
    return success_response(data=saved, message="Crop registered and calendar generated!")


@crop_bp.route("/api/crops/my-crops", methods=["GET"])
@optional_auth
def get_user_crops():
    user_id = request.user["id"] if getattr(request, "user", None) else "guest-farmer"
    crops = supabase_service.get_user_crops(user_id)
    return success_response(crops=crops)


@crop_bp.route("/api/crops/monitor", methods=["GET"])
def monitor_crop():
    crop_name = request.args.get("crop", request.args.get("crop_name", "Rice"))
    sowing_date = request.args.get("sowing_date")
    
    status = crop_calendar.monitor_crop_progress(crop_name, sowing_date)
    return success_response(status=status)


@crop_bp.route("/api/crops/monitoring", methods=["POST"])
@optional_auth
def log_crop_monitoring():
    data = request.get_json(silent=True) or {}
    if not data.get("crop_id"):
        return error_response("Crop ID is required", status_code=400)
        
    user_id = request.user["id"] if getattr(request, "user", None) else "guest-farmer"
    record = supabase_service.add_crop_monitoring(user_id, data)
    return success_response(data=record, message="Crop observation recorded!")
