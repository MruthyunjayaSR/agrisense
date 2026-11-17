from flask import Blueprint, request
from backend.services.supabase_service import supabase_service
from backend.utils.auth_middleware import require_auth
from backend.utils.validators import validate_email
from backend.utils.helpers import success_response, error_response
import uuid

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    phone = data.get("phone", "").strip()

    if not first_name:
        return error_response("First name is required", status_code=400)
    if not validate_email(email):
        return error_response("Please enter a valid email address", status_code=400)
    if len(password) < 8:
        return error_response("Password must be at least 8 characters long", status_code=400)

    # 1. Register with Supabase if client is active
    if supabase_service.is_configured and supabase_service.client:
        try:
            res = supabase_service.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "farmer_experience_level": "Beginner",
                        "preferred_language": "en"
                    }
                }
            })
            if res.user:
                token = res.session.access_token if res.session else "token-" + str(uuid.uuid4())
                return success_response(
                    message="Registration successful! Please check your email or proceed to login.",
                    user={"id": res.user.id, "email": res.user.email, "first_name": first_name},
                    token=token
                )
        except Exception as e:
            return error_response(str(e), status_code=400)

    # 2. Local Fallback for offline development/testing
    mock_id = str(uuid.uuid4())
    mock_token = f"agri-token-{mock_id[:8]}"
    return success_response(
        message="Registration successful!",
        user={"id": mock_id, "email": email, "first_name": first_name, "last_name": last_name, "phone": phone},
        token=mock_token
    )


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    remember = data.get("remember", False)

    if not email:
        return error_response("Email / Phone is required", status_code=400)
    if not password:
        return error_response("Password is required", status_code=400)

    # 1. Supabase auth if configured
    if supabase_service.is_configured and supabase_service.client:
        try:
            res = supabase_service.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if res.user and res.session:
                return success_response(
                    message="Signed in successfully!",
                    user={"id": res.user.id, "email": res.user.email},
                    token=res.session.access_token
                )
        except Exception as e:
            return error_response("Invalid email or password. Please verify credentials.", status_code=401)

    # 2. Local Fallback for offline dev
    mock_id = "farmer-uid-001"
    mock_token = "agri-token-farmer-001"
    first_name = email.split("@")[0].capitalize()
    return success_response(
        message="Signed in successfully!",
        user={"id": mock_id, "email": email, "first_name": first_name, "farmer_experience_level": "Beginner"},
        token=mock_token
    )


@auth_bp.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()

    if not validate_email(email):
        return error_response("Please enter a valid email", status_code=400)

    if supabase_service.is_configured and supabase_service.client:
        try:
            supabase_service.client.auth.reset_password_for_email(email)
        except Exception as e:
            print(f"[Auth] Supabase reset password error: {e}")

    return success_response(message="Password reset link sent! Please check your email inbox.")


@auth_bp.route("/api/auth/profile", methods=["GET"])
@require_auth
def get_profile():
    profile = supabase_service.get_profile(request.user["id"])
    return success_response(profile=profile)


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    return success_response(message="Signed out successfully.")
