# Copy this file to config_local.py and fill in your values

# Validation to ensure this template doesn't contain real credentials
def _validate_template():
    """Ensure this template doesn't contain real credentials"""
    if not isinstance(CALENDAR_IDS, list):
        raise ValueError("CALENDAR_IDS must be a list")
    
    for calendar_id in CALENDAR_IDS:
        if not calendar_id.startswith("your_calendar_id"):
            raise ValueError("Template contains non-placeholder calendar ID")
    
    if not SERVICE_ACCOUNT_KEY.startswith("{\"type\": \"service_account\""):
        raise ValueError("Template contains real service account key")

# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# Google Calendar API Configuration
CALENDAR_IDS = [
    "your_calendar_id_1@group.calendar.google.com",
    "your_calendar_id_2@group.calendar.google.com"
]

# Service Account JSON key (paste the entire contents of your service account JSON key file)
SERVICE_ACCOUNT_KEY = """{
    "type": "service_account",
    "project_id": "your_project_id",
    "private_key_id": "your_private_key_id",
    "private_key": "your_private_key",
    "client_email": "your_service_account_email",
    "client_id": "your_client_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your_cert_url"
}"""

# Run validation
_validate_template() 