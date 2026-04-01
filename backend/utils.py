import re
from functools import wraps
from flask import request, jsonify


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"


def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Username is valid"


def validate_request(data, required_fields):
    """Validate that all required fields are present"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True


def rate_limit(max_requests=100, window=3600):
    """
    Simple rate limiting decorator
    max_requests: maximum number of requests
    window: time window in seconds
    """
    requests_dict = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            if ip in requests_dict:
                requests_dict[ip] = [
                    req_time for req_time in requests_dict[ip]
                    if current_time - req_time < window
                ]
            else:
                requests_dict[ip] = []
            
            # Check rate limit
            if len(requests_dict[ip]) >= max_requests:
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded'
                }), 429
            
            # Add current request
            requests_dict[ip].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove potential XSS
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text.strip()


import time  # For rate_limit function