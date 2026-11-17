import re

def validate_crop_recommendation_input(data):
    """Validate N, P, K, temperature, humidity, pH, rainfall, season"""
    errors = []
    
    required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required numeric field: '{field}'")
        else:
            try:
                val = float(data[field])
                if field == 'ph' and not (0 <= val <= 14):
                    errors.append("Soil pH must be between 0 and 14")
                if field in ['N', 'P', 'K', 'rainfall'] and val < 0:
                    errors.append(f"{field} cannot be negative")
                if field == 'humidity' and not (0 <= val <= 100):
                    errors.append("Humidity must be between 0% and 100%")
            except (ValueError, TypeError):
                errors.append(f"Field '{field}' must be a valid number")
                
    return len(errors) == 0, errors


def validate_price_prediction_input(data):
    """Validate crop, month, rainfall, temperature, days_ahead"""
    errors = []
    if not data.get('crop'):
        errors.append("Crop name is required")
        
    month = data.get('month')
    if month is not None:
        try:
            m = int(month)
            if not (1 <= m <= 12):
                errors.append("Month must be between 1 and 12")
        except (ValueError, TypeError):
            errors.append("Month must be an integer between 1 and 12")
            
    days_ahead = data.get('days_ahead')
    if days_ahead is not None:
        try:
            d = int(days_ahead)
            if d not in [7, 14, 30]:
                errors.append("Days ahead should be 7, 14, or 30 days")
        except (ValueError, TypeError):
            errors.append("Days ahead must be an integer")
            
    return len(errors) == 0, errors


def validate_deal_request(data):
    """Validate direct market deal negotiation request"""
    errors = []
    name = data.get('farmer_name') or data.get('name')
    phone = data.get('phone')
    company = data.get('company_name') or data.get('company')
    
    if not name or not str(name).strip():
        errors.append("Farmer name is required")
    if not phone or not str(phone).strip():
        errors.append("Contact phone number is required")
    if not company or not str(company).strip():
        errors.append("Target company name is required")
        
    return len(errors) == 0, errors


def validate_email(email):
    """Simple email regex validator"""
    if not email:
        return False
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))
