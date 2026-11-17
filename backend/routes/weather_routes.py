from flask import Blueprint, request
from backend.services.weather_service import weather_service
from backend.utils.helpers import success_response

weather_bp = Blueprint("weather_bp", __name__)

@weather_bp.route("/api/weather/current", methods=["GET"])
def current_weather():
    location = request.args.get("location", "Nashik")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    
    weather_data = weather_service.get_current_weather(location=location, lat=lat, lon=lon)
    return success_response(**weather_data)


@weather_bp.route("/api/weather/forecast", methods=["GET"])
def weather_forecast():
    location = request.args.get("location", "Nashik")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    
    weather_data = weather_service.get_current_weather(location=location, lat=lat, lon=lon)
    return success_response(forecast=weather_data)
