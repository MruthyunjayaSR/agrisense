from flask import Blueprint, request
from backend.models.crop_calendar import crop_calendar
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth
from backend.utils.helpers import success_response, error_response

calendar_bp = Blueprint("calendar_bp", __name__)

@calendar_bp.route("/api/calendar/events", methods=["GET"])
def get_calendar_events():
    """
    Directly satisfies index.html calendar widget API call:
    GET /api/calendar/events?crop=Rice
    """
    crop = request.args.get("crop", "Rice")
    events = crop_calendar.get_frontend_calendar_events(crop)
    return success_response(events=events, crop=crop)


@calendar_bp.route("/api/calendar/generate", methods=["POST"])
@optional_auth
def generate_calendar():
    data = request.get_json(silent=True) or {}
    crop_name = data.get("crop_name", "Rice")
    sowing_date = data.get("sowing_date")
    variety = data.get("crop_variety", "Standard")
    
    user_id = request.user["id"] if getattr(request, "user", None) else None
    
    calendar_plan = crop_calendar.generate_full_crop_calendar(
        crop_name=crop_name,
        sowing_date_str=sowing_date,
        variety=variety,
        user_id=user_id,
        farm_id=data.get("farm_id")
    )
    
    if user_id:
        supabase_service.save_calendar_tasks(calendar_plan["tasks"])
        
    return success_response(calendar=calendar_plan, message="Calendar schedule generated successfully!")


@calendar_bp.route("/api/calendar/tasks", methods=["GET"])
@optional_auth
def get_calendar_tasks():
    user_id = request.user["id"] if getattr(request, "user", None) else None
    crop_id = request.args.get("crop_id")
    
    tasks = supabase_service.get_calendar_tasks(user_id=user_id, crop_id=crop_id)
    return success_response(tasks=tasks)


@calendar_bp.route("/api/calendar/tasks/<task_id>", methods=["PATCH"])
@optional_auth
def update_task_status(task_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "Completed")
    
    updates = {
        "status": status,
        "completed_at": None if status == "Pending" else "now()"
    }
    updated = supabase_service.update_calendar_task(task_id, updates)
    return success_response(task=updated, message=f"Task updated to {status}")
