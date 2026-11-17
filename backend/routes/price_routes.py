from flask import Blueprint, request
from backend.models.price_prediction import price_model
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import optional_auth
from backend.utils.validators import validate_price_prediction_input
from backend.utils.helpers import success_response, error_response

price_bp = Blueprint("price_bp", __name__)

@price_bp.route("/api/price/predict", methods=["POST"])
@optional_auth
def predict_price():
    data = request.get_json(silent=True) or {}
    
    valid, errors = validate_price_prediction_input(data)
    if not valid:
        return error_response("Invalid input parameters", errors=errors, status_code=400)
        
    crop = data.get("crop", "Tomato")
    month = int(data.get("month", 7))
    rainfall = float(data.get("rainfall", 120))
    temp = float(data.get("temperature", 28))
    days_ahead = int(data.get("days_ahead", 7))
    
    result = price_model.predict_forecast(
        crop=crop,
        month=month,
        rainfall=rainfall,
        temperature=temp,
        days_ahead=days_ahead
    )
    
    # Save to Supabase price_predictions table
    user_id = request.user["id"] if getattr(request, "user", None) else None
    supabase_service.save_price_prediction(
        user_id=user_id,
        crop_name=crop,
        market=result["market"],
        current_price=result["current_price"],
        forecast_data=result["forecast"],
        best_date=result["best_day"]["date"],
        best_price=result["best_day"]["price"]
    )
    
    # Match frontend expectations in index.html directly
    return success_response(**result)


@price_bp.route("/api/market/live", methods=["GET"])
def live_market_prices():
    crop_filter = request.args.get("crop", "all")
    market_data = price_model.get_live_market_data(crop_filter)
    return success_response(**market_data)
