import logging

def setup_logging():
    """Configure logging with safe defaults"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create loggers for each module
    loggers = {
        'calendar': logging.getLogger('calendar'),
        'neopixel': logging.getLogger('neopixel'),
        'time': logging.getLogger('time'),
        'main': logging.getLogger('main')
    }
    
    return loggers

def sanitize_calendar_id(calendar_id):
    """Sanitize calendar ID for logging"""
    if not calendar_id:
        return "None"
    parts = calendar_id.split('@')
    if len(parts) > 1:
        return f"{parts[0][:3]}...@{parts[1]}"
    return f"{calendar_id[:3]}..."

def sanitize_error(error):
    """Sanitize error messages that might contain sensitive data"""
    error_str = str(error)
    # List of patterns to sanitize
    sensitive_patterns = [
        (r'client_email":"[^"]+', 'client_email":"[REDACTED]'),
        (r'private_key":"[^"]+', 'private_key":"[REDACTED]'),
        (r'refresh_token":"[^"]+', 'refresh_token":"[REDACTED]'),
        (r'access_token":"[^"]+', 'access_token":"[REDACTED]'),
        (r'Bearer [^"]+', 'Bearer [REDACTED]'),
        # Add email pattern
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]'),
    ]
    
    for pattern, replacement in sensitive_patterns:
        error_str = error_str.replace(pattern, replacement)
    
    return error_str 