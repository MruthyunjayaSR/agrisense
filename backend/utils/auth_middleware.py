from functools import wraps
from flask import request
from backend.services.supabase_service import supabase_service
from backend.utils.helpers import error_response

def require_auth(f):
    """
    Decorator to protect routes requiring Supabase Authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            
        if not token:
            # Check query param as fallback
            token = request.args.get("token")
            
        if not token:
            return error_response(
                message="Authentication required. Please sign in.",
                status_code=401
            )
            
        user = supabase_service.verify_token(token)
        if not user:
            return error_response(
                message="Invalid or expired session. Please sign in again.",
                status_code=401
            )
            
        # Attach verified user to request context
        request.user = user
        return f(*args, **kwargs)
        
    return decorated_function


def optional_auth(f):
    """
    Decorator for endpoints that can benefit from user context if present,
    but still allow anonymous guest requests.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        elif "token" in request.args:
            token = request.args.get("token")
            
        request.user = supabase_service.verify_token(token) if token else None
        return f(*args, **kwargs)
        
    return decorated_function
