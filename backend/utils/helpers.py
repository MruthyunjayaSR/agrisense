from flask import jsonify

def success_response(data=None, message="Success", status_code=200, **kwargs):
    """Generate consistent JSON success response"""
    payload = {
        "success": True,
        "message": message
    }
    if data is not None:
        if isinstance(data, dict):
            payload.update(data)
        else:
            payload["data"] = data
            
    # Include any additional keyword arguments directly
    for k, v in kwargs.items():
        payload[k] = v
        
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, errors=None, **kwargs):
    """Generate consistent JSON error response"""
    payload = {
        "success": False,
        "message": message
    }
    if errors is not None:
        payload["errors"] = errors
        
    for k, v in kwargs.items():
        payload[k] = v
        
    return jsonify(payload), status_code
