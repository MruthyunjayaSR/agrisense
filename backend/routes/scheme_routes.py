from flask import Blueprint
from backend.services.supabase_service import supabase_service
from backend.utils.helpers import success_response

scheme_bp = Blueprint("scheme_bp", __name__)

@scheme_bp.route("/api/schemes", methods=["GET"])
def get_schemes():
    schemes = supabase_service.get_government_schemes()
    # Satisfies index.html loadSchemes() which iterates through d.schemes
    return success_response(schemes=schemes)
