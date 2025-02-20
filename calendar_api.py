import urequests as requests
import json
import time
import jwt
import config
from time_manager import TimeManager
from log_config import sanitize_calendar_id, sanitize_error

class CalendarAPI:
    def __init__(self, time_manager, logger):
        self.time_manager = time_manager
        self.token = None
        self.token_expires = 0
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.logger = logger
        
    def _get_jwt_token(self):
        """Create a JWT token for service account authentication"""
        try:
            self.logger.debug("Generating new JWT token")
            current_time = self.time_manager.get_utc_timestamp()
            key_data = json.loads(config.SERVICE_ACCOUNT_KEY)
            
            # Create JWT claims
            claims = {
                "iss": key_data["client_email"],
                "scope": "https://www.googleapis.com/auth/calendar.readonly",
                "aud": "https://oauth2.googleapis.com/token",
                "exp": current_time + 3600,
                "iat": current_time
            }
            
            # Create and sign JWT using the micropython-jwt package
            token = jwt.encode(claims, key_data["private_key"], algorithm="RS256")
            self.logger.debug("JWT token generated successfully")
            return token
            
        except Exception as e:
            self.logger.error(f"Error creating JWT token: {sanitize_error(e)}")
            return None
            
    def _get_access_token(self):
        """Get access token using service account JWT"""
        try:
            self.logger.debug("Getting new access token")
            jwt_token = self._get_jwt_token()
            if not jwt_token:
                return False
                
            url = "https://oauth2.googleapis.com/token"
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_token
            }
            
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result["access_token"]
                self.token_expires = self.time_manager.get_utc_timestamp() + result["expires_in"]
                self.logger.info("Successfully obtained new access token")
                return True
            self.logger.error(f"Failed to get access token. Status code: {response.status_code}")
            return False
        except Exception as e:
            self.logger.error(f"Error getting access token: {sanitize_error(e)}")
            return False
        finally:
            response.close()
            
    def _ensure_token(self):
        """Ensure we have a valid access token"""
        if not self.token or self.time_manager.get_utc_timestamp() >= self.token_expires:
            self.logger.debug("Token expired or missing, refreshing...")
            return self._get_access_token()
        return True
        
    def get_calendar_status(self):
        """Get current and upcoming events from all calendars"""
        if not self._ensure_token():
            self.logger.error("Failed to ensure valid token")
            return None, 0, None
            
        try:
            # Ensure time is synced
            if not self.time_manager.ensure_time_synced():
                self.logger.warning("Time sync failed")
                
            # Calculate time range
            now = self.time_manager.get_utc_timestamp()
            timeMin = self.time_manager.format_utc_datetime(now)
            timeMax = self.time_manager.format_utc_datetime(now + 10800)  # 3 hours ahead
            
            all_events = []
            
            # Fetch events from all calendars
            for calendar_id in config.CALENDAR_IDS:
                try:
                    safe_id = sanitize_calendar_id(calendar_id)
                    self.logger.debug(f"Fetching events for calendar: {safe_id}")
                    
                    url = f"{self.base_url}/calendars/{calendar_id}/events"
                    params = {
                        "timeMin": timeMin,
                        "timeMax": timeMax,
                        "singleEvents": "true",
                        "orderBy": "startTime"
                    }
                    
                    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    url = f"{url}?{param_str}"
                    
                    headers = {"Authorization": f"Bearer {self.token}"}
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        calendar_events = response.json().get("items", [])
                        self.logger.debug(f"Found {len(calendar_events)} events in calendar {safe_id}")
                        all_events.extend(calendar_events)
                    else:
                        self.logger.error(f"Error fetching calendar {safe_id}: {response.status_code}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing calendar {safe_id}: {sanitize_error(e)}")
                finally:
                    response.close()
                    
            # Sort all events by start time
            all_events.sort(key=lambda x: x["start"]["dateTime"])
            self.logger.info(f"Processing {len(all_events)} total events")
            
            current_time = self.time_manager.get_utc_timestamp()
            total_remaining = 0
            is_busy = False
            next_meeting_in = None
            
            # Process all events
            for event in all_events:
                start_time = self.time_manager.parse_datetime(event["start"]["dateTime"])
                end_time = self.time_manager.parse_datetime(event["end"]["dateTime"])
                
                # If event is happening now
                if start_time <= current_time <= end_time:
                    is_busy = True
                    remaining = (end_time - current_time) / 60  # Convert to minutes
                    total_remaining = remaining
                    
                    # Check for back-to-back meetings
                    next_event_idx = all_events.index(event) + 1
                    while next_event_idx < len(all_events):
                        next_event = all_events[next_event_idx]
                        next_start = self.time_manager.parse_datetime(next_event["start"]["dateTime"])
                        next_end = self.time_manager.parse_datetime(next_event["end"]["dateTime"])
                        
                        # If less than 5 minutes between meetings
                        if (next_start - end_time) <= 300:
                            additional_time = (next_end - next_start) / 60
                            total_remaining += additional_time
                            end_time = next_end
                            self.logger.debug("Found back-to-back meeting")
                        else:
                            break
                        next_event_idx += 1
                    
                    self.logger.info(f"Currently busy with {int(total_remaining)} minutes remaining")
                    return is_busy, int(total_remaining), None
                
                # If this is a future event
                elif start_time > current_time:
                    minutes_until = (start_time - current_time) / 60
                    if next_meeting_in is None or minutes_until < next_meeting_in:
                        next_meeting_in = int(minutes_until)
            
            if next_meeting_in is not None:
                self.logger.info(f"Next meeting in {next_meeting_in} minutes")
            else:
                self.logger.info("No upcoming meetings")
                
            return is_busy, 0, next_meeting_in
            
        except Exception as e:
            self.logger.error(f"Error checking calendars: {sanitize_error(e)}")
            return None, 0, None 