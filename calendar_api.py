import urequests as requests
import json
import time
import config
from time_manager import TimeManager

class CalendarAPI:
    def __init__(self, time_manager):
        self.token = None
        self.token_expires = 0
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.time_manager = time_manager
        
    def _refresh_token(self):
        """Refresh the access token using the refresh token"""
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,
                "refresh_token": config.REFRESH_TOKEN,
                "grant_type": "refresh_token"
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result["access_token"]
                self.token_expires = self.time_manager.get_utc_timestamp() + result["expires_in"]
                return True
            return False
        except Exception as e:
            print("Error refreshing token:", e)
            return False
        finally:
            response.close()

    def _ensure_token(self):
        """Ensure we have a valid token"""
        if not self.token or self.time_manager.get_utc_timestamp() >= self.token_expires:
            return self._refresh_token()
        return True

    def get_calendar_status(self):
        """Get current and upcoming events with timing information"""
        if not self._ensure_token():
            return None, 0, None

        try:
            # Ensure time is synced before making API calls
            if not self.time_manager.ensure_time_synced():
                print("Warning: Time sync failed")
            
            # Calculate time range (now to 3 hours ahead)
            now = self.time_manager.get_utc_timestamp()
            timeMin = self.time_manager.format_utc_datetime(now)
            timeMax = self.time_manager.format_utc_datetime(now + 10800)  # 3 hours ahead

            # Build URL with parameters
            url = f"{self.base_url}/calendars/{config.CALENDAR_ID}/events"
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
                events = response.json().get("items", [])
                current_time = self.time_manager.get_utc_timestamp()
                total_remaining = 0
                is_busy = False
                next_meeting_in = None
                
                for event in events:
                    start_time = self.time_manager.parse_datetime(event["start"]["dateTime"])
                    end_time = self.time_manager.parse_datetime(event["end"]["dateTime"])
                    
                    # If event is happening now
                    if start_time <= current_time <= end_time:
                        is_busy = True
                        remaining = (end_time - current_time) / 60  # Convert to minutes
                        total_remaining = remaining
                        
                        # Check for back-to-back meetings
                        next_event_idx = events.index(event) + 1
                        while next_event_idx < len(events):
                            next_event = events[next_event_idx]
                            next_start = self.time_manager.parse_datetime(next_event["start"]["dateTime"])
                            next_end = self.time_manager.parse_datetime(next_event["end"]["dateTime"])
                            
                            # If there's less than 5 minutes between meetings, consider it back-to-back
                            if (next_start - end_time) <= 300:  # 5 minutes in seconds
                                additional_time = (next_end - next_start) / 60
                                total_remaining += additional_time
                                end_time = next_end  # Update for next iteration
                            else:
                                break
                            next_event_idx += 1
                        
                        return is_busy, int(total_remaining), None
                    
                    # If this is a future event, calculate time until it starts
                    elif start_time > current_time:
                        minutes_until = (start_time - current_time) / 60
                        if next_meeting_in is None or minutes_until < next_meeting_in:
                            next_meeting_in = int(minutes_until)
                
                return is_busy, 0, next_meeting_in
            
            return None, 0, None
            
        except Exception as e:
            print("Error checking calendar:", e)
            return None, 0, None
        finally:
            response.close() 