from flask import Blueprint, request
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth
from backend.utils.validators import validate_deal_request
from backend.utils.helpers import success_response, error_response

market_bp = Blueprint("market_bp", __name__)

@market_bp.route("/api/market/deal-request", methods=["POST"])
@optional_auth
def submit_deal_request():
    data = request.get_json(silent=True) or {}
    
    valid, errors = validate_deal_request(data)
    if not valid:
        return error_response("Please fill all required deal fields", errors=errors, status_code=400)
        
    user_id = request.user["id"] if getattr(request, "user", None) else None
    data["user_id"] = user_id
    
    saved_deal = supabase_service.save_deal_request(data)
    
    return success_response(
        deal=saved_deal,
        message="Deal request submitted successfully! Procurement team will contact you within 24 hours."
    )


@market_bp.route("/api/market/deal-requests", methods=["GET"])
@optional_auth
def get_deal_requests():
    user_id = request.user["id"] if getattr(request, "user", None) else None
    deals = supabase_service.get_deal_requests(user_id)
    return success_response(deals=deals)
