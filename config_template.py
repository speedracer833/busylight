# Copy this file to config_local.py and fill in your values

# Validation to ensure this template doesn't contain real credentials
def _validate_template():
    """Ensure this template doesn't contain real credentials"""
    credentials = [WIFI_SSID, WIFI_PASSWORD, CALENDAR_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]
    placeholders = ["your_wifi_ssid", "your_wifi_password", "your_calendar_id@group.calendar.google.com",
                   "your_client_id", "your_client_secret", "your_refresh_token"]
    
    if credentials != placeholders:
        raise ValueError("Template contains non-placeholder values. Please reset to defaults.")

# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# Google Calendar API Configuration
CALENDAR_ID = "your_calendar_id@group.calendar.google.com"  # Usually your email for primary calendar
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REFRESH_TOKEN = "your_refresh_token"

# Run validation
_validate_template() 